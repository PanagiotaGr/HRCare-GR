from __future__ import annotations

from app.graph.state import ActivityStatus, GraphState, InteractionTurn
from app.utils.config import get_settings
from app.utils.llm import get_llm


def check_progress(state: GraphState, patient_reply: str, record_reply: bool = True) -> GraphState:
    if state.current_activity_id is None:
        return state

    settings = get_settings()
    llm = get_llm(settings.llm_provider)
    if record_reply:
        state.conversation.append(InteractionTurn(speaker="patient", text=patient_reply))

    activity = next(a for a in state.activities if a.id == state.current_activity_id)
    if llm.assess_progress(patient_reply):
        activity.status = ActivityStatus.DONE
        state.conversation.append(InteractionTurn(speaker="system", text=f"Activity {activity.id} marked as done."))
    else:
        activity.status = ActivityStatus.SKIPPED
        state.conversation.append(InteractionTurn(speaker="system", text=f"Activity {activity.id} marked as skipped."))

    state.current_activity_id = None
    return state
