from __future__ import annotations

from app.graph.state import ActivityStatus, GraphState


def select_next_activity(state: GraphState) -> GraphState:
    for activity in state.activities:
        if activity.status == ActivityStatus.PENDING:
            state.current_activity_id = activity.id
            activity.status = ActivityStatus.IN_PROGRESS
            return state
    state.current_activity_id = None
    return state
