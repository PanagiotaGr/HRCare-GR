from __future__ import annotations

from app.graph.state import GraphState
from app.memory.patient_memory import attach_memory_to_state, update_memory_from_state
from app.nodes.knowledge_retriever import retrieve_knowledge
from app.nodes.planner import plan_activities
from app.nodes.robot_response import produce_robot_response
from app.nodes.situation_assessor import select_next_activity
from app.nodes.task_generator import generate_tasks


def initialize_daily_plan(state: GraphState, include_memory: bool = True) -> GraphState:
    state = retrieve_knowledge(state)
    if include_memory:
        state = attach_memory_to_state(state)
    state = generate_tasks(state)
    state = plan_activities(state)
    return state


def run_next_robot_turn(state: GraphState) -> GraphState:
    state = select_next_activity(state)
    state = produce_robot_response(state)
    return state


def finalize_session(state: GraphState, persist_memory: bool = True) -> GraphState:
    if persist_memory:
        update_memory_from_state(state)
    return state
