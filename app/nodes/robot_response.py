from __future__ import annotations

from app.graph.state import GraphState, InteractionTurn
from app.utils.config import get_settings
from app.utils.llm import get_llm


def produce_robot_response(state: GraphState) -> GraphState:
    if state.patient is None or state.current_activity_id is None:
        return state

    activity = next(a for a in state.activities if a.id == state.current_activity_id)
    settings = get_settings()
    llm = get_llm(settings.llm_provider)
    text = llm.generate_robot_message(activity.title, state.patient.name, state.patient.language)
    state.conversation.append(InteractionTurn(speaker="robot", text=text))
    return state
