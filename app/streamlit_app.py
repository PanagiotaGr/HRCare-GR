from __future__ import annotations

import pandas as pd
import streamlit as st

from app.graph.state import ActivityStatus, GraphState, InteractionTurn
from app.graph.workflow import initialize_daily_plan, run_next_robot_turn
from app.nodes.progress_checker import check_progress
from app.utils.config import get_settings
from app.utils.llm import get_llm
from app.utils.logging import save_session_log
from app.utils.mood import detect_mood
from app.utils.public_adl import load_adl_scenarios, load_adl_templates
from app.utils.reporting import caregiver_recommendation, summarize_session


st.set_page_config(page_title="CareMate | HRCare-GR", page_icon="💙", layout="wide")

st.markdown(
    """
    <style>
    .big-card {
        border-radius: 24px;
        padding: 2rem;
        background: #f5f8ff;
        border: 1px solid #dbe7ff;
        margin-bottom: 1rem;
    }
    .elder-title {font-size: 2.4rem; font-weight: 800; margin-bottom: .5rem;}
    .elder-text {font-size: 1.6rem; line-height: 1.5;}
    .robot-face {font-size: 4rem; text-align: center;}
    .help-card {
        border-radius: 24px;
        padding: 1.5rem;
        background: #fff5f5;
        border: 2px solid #ffb3b3;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💙 CareMate")
st.caption("Friendly elder interface powered by the HRCare-GR research system")
st.warning(
    "Research demo only: this system uses synthetic/anonymized profiles and must not be used for real medical decisions."
)

settings = get_settings()
adl_scenarios = load_adl_scenarios()
adl_templates = load_adl_templates()
scenario_options = {f"{s['title']} ({s['id']})": s for s in adl_scenarios}

with st.sidebar:
    st.header("Simulation settings")
    patient_id = st.selectbox("Patient", ["P001", "P002"])
    scenario_label = st.selectbox("Public ADL scenario", list(scenario_options.keys()))
    selected_scenario = scenario_options[scenario_label]
    simulation_time = st.text_input("Start time", value=selected_scenario["events"][0]["time"])
    doctor_instructions = st.text_area(
        "Doctor instructions",
        value=selected_scenario["robot_goal"],
        placeholder="π.χ. Υπενθύμιση φυσικοθεραπείας στις 12:00",
    )
    provider = st.selectbox("LLM provider", ["mock", "openai"], index=0 if settings.llm_provider == "mock" else 1)
    model = st.text_input("LLM model", value=settings.llm_model)
    st.info("OpenAI mode requires OPENAI_API_KEY in your .env file.")


def activity_table(state: GraphState) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Time": a.preferred_time,
                "Activity": a.title,
                "Category": a.category,
                "Priority": a.priority,
                "Critical": "Yes" if a.safety_critical else "No",
                "Status": a.status.value,
            }
            for a in state.activities
        ]
    )


def scenario_event_table(scenario: dict) -> pd.DataFrame:
    return pd.DataFrame(scenario["events"])


def current_or_next_activity(state: GraphState):
    if state.current_activity_id:
        return next((a for a in state.activities if a.id == state.current_activity_id), None)
    return next((a for a in state.activities if a.status == ActivityStatus.PENDING), None)


def status_icon(status: ActivityStatus) -> str:
    return {
        ActivityStatus.DONE: "✅",
        ActivityStatus.SKIPPED: "⏰",
        ActivityStatus.IN_PROGRESS: "🟡",
        ActivityStatus.PENDING: "⚪",
    }[status]


def activity_emoji(category: str) -> str:
    return {
        "medication": "💊",
        "meal": "🍽️",
        "exercise": "🚶",
        "hydration": "💧",
        "social": "💬",
        "monitoring": "🩺",
    }.get(category, "📌")


if "state" not in st.session_state:
    st.session_state.state = None
if "last_mood" not in st.session_state:
    st.session_state.last_mood = detect_mood("")
if "emergency_events" not in st.session_state:
    st.session_state.emergency_events = []

if st.button("Generate / Reset daily plan", type="primary"):
    state = GraphState(
        patient_id=patient_id,
        doctor_instructions=doctor_instructions,
        simulation_time=simulation_time,
    )
    state = initialize_daily_plan(state)
    state.retrieved_notes.append(f"Selected ADL scenario: {selected_scenario['title']} — {selected_scenario['robot_goal']}")
    st.session_state.state = state
    st.session_state.provider = provider
    st.session_state.model = model
    st.session_state.selected_scenario = selected_scenario
    st.session_state.last_mood = detect_mood("")
    st.session_state.emergency_events = []
    st.success("Daily plan generated.")

state: GraphState | None = st.session_state.state

if state is None:
    st.warning("Generate a daily plan to start the CareMate simulation.")
    st.stop()

active_scenario = st.session_state.get("selected_scenario", selected_scenario)
active_activity = current_or_next_activity(state)
summary = summarize_session(state, st.session_state.last_mood.label)
completion_ratio = summary["completion_rate"] / 100 if summary["total_tasks"] else 0
patient_name = state.patient.name if state.patient else state.patient_id

tab_elder, tab_caregiver, tab_research = st.tabs(["👵 Elder Mode", "👩‍⚕️ Caregiver Dashboard", "📊 Research View"])

with tab_elder:
    col_avatar, col_task = st.columns([0.25, 0.75])
    with col_avatar:
        st.markdown(f"<div class='robot-face'>{st.session_state.last_mood.emoji}</div>", unsafe_allow_html=True)
        st.progress(completion_ratio)
        st.write(f"**Πρόοδος:** {summary['completed_tasks']} / {summary['total_tasks']}")

    with col_task:
        greeting = f"Καλημέρα, {patient_name}!"
        if active_activity:
            st.markdown(
                f"""
                <div class='big-card'>
                  <div class='elder-title'>{activity_emoji(active_activity.category)} {greeting}</div>
                  <div class='elder-text'>Ώρα για: <strong>{active_activity.title}</strong></div>
                  <div class='elder-text'>Θα το κάνουμε ήρεμα, βήμα-βήμα.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class='big-card'>
                  <div class='elder-title'>🎉 Μπράβο, {patient_name}!</div>
                  <div class='elder-text'>Το σημερινό πρόγραμμα ολοκληρώθηκε.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    with action_col1:
        if st.button("✅ Το έκανα", use_container_width=True):
            if active_activity and not state.current_activity_id:
                state.current_activity_id = active_activity.id
                active_activity.status = ActivityStatus.IN_PROGRESS
            state = check_progress(state, "ναι έγινε", record_reply=True)
            st.session_state.last_mood = detect_mood("ναι έγινε")
            st.session_state.state = state
            st.rerun()
    with action_col2:
        if st.button("⏰ Σε λίγο", use_container_width=True):
            if active_activity:
                active_activity.status = ActivityStatus.SKIPPED
                state.conversation.append(InteractionTurn(speaker="patient", text="Σε λίγο"))
                state.conversation.append(InteractionTurn(speaker="robot", text="Εντάξει. Θα το κρατήσω ως εκκρεμότητα και θα συνεχίσουμε ήρεμα."))
                st.session_state.state = state
                st.rerun()
    with action_col3:
        if st.button("🔊 Άκου", use_container_width=True):
            if active_activity:
                st.info(f"CareMate: {patient_name}, ήρθε η ώρα για {active_activity.title}. Θα το κάνουμε μαζί, ήρεμα.")
            else:
                st.info("CareMate: Το σημερινό πρόγραμμα ολοκληρώθηκε. Μπράβο!")
    with action_col4:
        if st.button("🆘 Βοήθεια", use_container_width=True):
            event = {"patient": patient_name, "scenario": active_scenario["id"], "activity": active_activity.title if active_activity else "none"}
            st.session_state.emergency_events.append(event)
            state.conversation.append(InteractionTurn(speaker="system", text="Emergency/help button pressed. Caregiver should be notified in a real deployment."))
            st.session_state.state = state
            st.error("Καταγράφηκε αίτημα βοήθειας. Στο πραγματικό σύστημα θα ειδοποιηθεί ο φροντιστής.")

    st.subheader("Σημερινή σειρά")
    for activity in state.activities:
        st.write(f"{status_icon(activity.status)} {activity.preferred_time} — {activity_emoji(activity.category)} {activity.title}")

    patient_message = st.chat_input("Γράψτε ή πείτε πώς νιώθετε")
    if patient_message:
        st.session_state.last_mood = detect_mood(patient_message)
        state.conversation.append(InteractionTurn(speaker="patient", text=patient_message))
        current_activity_name = active_activity.title if active_activity else None
        try:
            llm = get_llm(
                provider=st.session_state.get("provider", provider),
                api_key=settings.openai_api_key,
                model=st.session_state.get("model", model),
            )
            robot_reply = llm.generate_chat_response(
                patient_name=patient_name,
                patient_message=patient_message,
                current_activity=current_activity_name,
                retrieved_notes=state.retrieved_notes,
                language=state.patient.language if state.patient else settings.language,
            )
        except Exception as exc:
            robot_reply = f"Δεν μπόρεσα να χρησιμοποιήσω το LLM ({exc}). Συνεχίζω σε mock mode."
        state.conversation.append(InteractionTurn(speaker="robot", text=robot_reply))
        st.session_state.state = state
        st.rerun()

    for turn in state.conversation[-6:]:
        with st.chat_message(turn.speaker):
            st.write(turn.text)

with tab_caregiver:
    st.subheader("Caregiver Dashboard")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Completion", f"{summary['completion_rate']}%")
    metric_cols[1].metric("Completed", summary["completed_tasks"])
    metric_cols[2].metric("Skipped", summary["skipped_tasks"])
    metric_cols[3].metric("Critical done", f"{summary['critical_completed']}/{summary['critical_total']}")
    metric_cols[4].metric("Mood", f"{st.session_state.last_mood.emoji} {st.session_state.last_mood.label}")

    if st.session_state.emergency_events:
        st.error(f"Help requests: {len(st.session_state.emergency_events)}")
        st.dataframe(pd.DataFrame(st.session_state.emergency_events), use_container_width=True, hide_index=True)

    st.info(caregiver_recommendation(summary))
    st.subheader("Daily plan status")
    st.dataframe(activity_table(state), use_container_width=True, hide_index=True)
    st.subheader("Recent conversation")
    for turn in state.conversation[-10:]:
        st.write(f"**{turn.speaker}:** {turn.text}")

with tab_research:
    st.subheader("Research View")
    st.write("This view exposes the underlying ADL scenario, knowledge layer, and structured simulation state.")
    st.subheader("Public ADL scenario")
    st.write(f"**Scenario:** {active_scenario['title']}")
    st.write(f"**Patient state:** {active_scenario['patient_state']}")
    st.write(f"**Robot goal:** {active_scenario['robot_goal']}")
    st.dataframe(scenario_event_table(active_scenario), use_container_width=True, hide_index=True)

    with st.expander("ADL activity knowledge layer"):
        st.write(adl_templates["description"])
        st.dataframe(pd.DataFrame(adl_templates["categories"]), use_container_width=True, hide_index=True)

    st.subheader("Session summary")
    st.json(summary)
    st.subheader("Safety warnings")
    if state.warnings:
        for warning in state.warnings:
            st.warning(warning)
    else:
        st.success("No safety warnings for this session.")

    if st.button("Save session log"):
        path = save_session_log(state, settings.log_dir)
        st.success(f"Saved: {path}")
