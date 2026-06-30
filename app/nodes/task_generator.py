from __future__ import annotations

from app.graph.state import Activity, GraphState


def generate_tasks(state: GraphState) -> GraphState:
    if state.patient is None:
        raise ValueError("Patient must be loaded before task generation.")

    activities = [
        Activity(
            id="a1",
            title="Πρωινό γεύμα",
            category="meal",
            preferred_time="08:30",
            duration_minutes=30,
            priority=4,
        ),
        Activity(
            id="a2",
            title="Υπενθύμιση πρωινού φαρμάκου",
            category="medication",
            preferred_time="09:00",
            duration_minutes=5,
            priority=5,
            safety_critical=True,
        ),
        Activity(
            id="a3",
            title="Ήπια άσκηση κινητικότητας",
            category="exercise",
            preferred_time="10:30",
            duration_minutes=20,
            priority=3,
        ),
        Activity(
            id="a4",
            title="Υπενθύμιση ενυδάτωσης",
            category="hydration",
            preferred_time="11:30",
            duration_minutes=5,
            priority=3,
        ),
    ]

    if "σάκχαρο" in " ".join(state.patient.constraints):
        activities.insert(
            0,
            Activity(
                id="a0",
                title="Έλεγχος σακχάρου πριν το πρωινό",
                category="monitoring",
                preferred_time="08:00",
                duration_minutes=10,
                priority=5,
                safety_critical=True,
            ),
        )

    if state.doctor_instructions.strip():
        activities.append(
            Activity(
                id="doctor_note",
                title=f"Οδηγία ιατρού: {state.doctor_instructions.strip()}",
                category="monitoring",
                preferred_time="12:00",
                duration_minutes=10,
                priority=5,
                safety_critical=True,
            )
        )

    state.activities = activities
    return state
