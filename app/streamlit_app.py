from __future__ import annotations

import pandas as pd
import streamlit as st

from app.graph.state import ActivityStatus, GraphState, InteractionTurn
from app.graph.workflow import initialize_daily_plan, run_next_robot_turn
from app.nodes.progress_checker import check_progress
from app.utils.config import get_settings
from app.utils.llm import get_llm
from app.utils.logging import save_session_log
from app.utils.public_adl import load_adl_scenarios, load_adl_templates


st.set_page_config(page_title="HRCare-GR", page_icon="🤖", layout="wide")

st.title("🤖 HRCare-GR")
st.caption("Hybrid LLM + rule-based assistive robot simulation for Greek elderly care")
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


if "state" not in st.session_state:
    st.session_state.state = None

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
    st.success("Daily plan generated.")

state: GraphState | None = st.session_state.state

if state is None:
    st.warning("Generate a daily plan to start the simulation.")
    st.stop()

active_scenario = st.session_state.get("selected_scenario", selected_scenario)

left, right = st.columns([1.1, 0.9])

with left:
    st.subheader("Patient profile")
    if state.patient:
        st.write(f"**Name:** {state.patient.name}")
        st.write(f"**Age:** {state.patient.age}")
        st.write("**Conditions:** " + ", ".join(state.patient.conditions))
        st.write("**Preferences:** " + ", ".join(state.patient.preferences))
        st.write("**Constraints:** " + ", ".join(state.patient.constraints))

    st.subheader("Public ADL scenario")
    st.write(f"**Scenario:** {active_scenario['title']}")
    st.write(f"**Patient state:** {active_scenario['patient_state']}")
    st.write(f"**Robot goal:** {active_scenario['robot_goal']}")
    st.dataframe(scenario_event_table(active_scenario), use_container_width=True, hide_index=True)

    st.subheader("Daily plan")
    st.dataframe(activity_table(state), use_container_width=True, hide_index=True)

    with st.expander("ADL activity knowledge layer"):
        st.write(adl_templates["description"])
        st.dataframe(pd.DataFrame(adl_templates["categories"]), use_container_width=True, hide_index=True)

    if state.warnings:
        st.subheader("Safety warnings")
        for warning in state.warnings:
            st.warning(warning)

with right:
    st.subheader("Robot interaction")

    if st.button("Robot: next activity"):
        st.session_state.state = run_next_robot_turn(state)
        state = st.session_state.state

    for turn in state.conversation:
        with st.chat_message(turn.speaker):
            st.write(turn.text)

    patient_message = st.chat_input("Patient reply")
    if patient_message:
        state.conversation.append(InteractionTurn(speaker="patient", text=patient_message))

        current_activity = None
        if state.current_activity_id:
            current_activity = next((a.title for a in state.activities if a.id == state.current_activity_id), None)

        try:
            llm = get_llm(
                provider=st.session_state.get("provider", provider),
                api_key=settings.openai_api_key,
                model=st.session_state.get("model", model),
            )
            robot_reply = llm.generate_chat_response(
                patient_name=state.patient.name if state.patient else state.patient_id,
                patient_message=patient_message,
                current_activity=current_activity,
                retrieved_notes=state.retrieved_notes,
                language=state.patient.language if state.patient else settings.language,
            )
        except Exception as exc:
            robot_reply = f"Δεν μπόρεσα να χρησιμοποιήσω το LLM ({exc}). Συνεχίζω σε mock mode."

        state.conversation.append(InteractionTurn(speaker="robot", text=robot_reply))

        if state.current_activity_id:
            state = check_progress(state, patient_message, record_reply=False)

        st.session_state.state = state
        st.rerun()

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    total = len(state.activities)
    done = sum(1 for a in state.activities if a.status == ActivityStatus.DONE)
    st.metric("Task completion", f"{done}/{total}")
with col2:
    skipped = sum(1 for a in state.activities if a.status == ActivityStatus.SKIPPED)
    st.metric("Skipped", skipped)
with col3:
    critical = sum(1 for a in state.activities if a.safety_critical)
    st.metric("Critical tasks", critical)

if st.button("Save session log"):
    path = save_session_log(state, settings.log_dir)
    st.success(f"Saved: {path}")
