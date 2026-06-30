from __future__ import annotations

from app.graph.state import GraphState
from app.rules.activity_rules import flag_safety_warnings, resolve_schedule_conflicts


def plan_activities(state: GraphState) -> GraphState:
    state.activities = resolve_schedule_conflicts(state.activities)
    state.warnings.extend(flag_safety_warnings(state.activities))
    return state
