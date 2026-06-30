from app.graph.state import Activity, ActivityStatus, GraphState
from app.utils.mood import detect_mood
from app.utils.reporting import summarize_session


def test_detect_mood_flags_negative_message():
    result = detect_mood("Δεν νιώθω καλά σήμερα")
    assert result.label == "Needs attention"
    assert result.confidence > 0.8


def test_session_summary_counts_completed_tasks():
    state = GraphState(patient_id="P001")
    state.activities = [
        Activity(id="a1", title="Breakfast", category="meal", preferred_time="08:00", status=ActivityStatus.DONE),
        Activity(id="a2", title="Medication", category="medication", preferred_time="09:00", status=ActivityStatus.SKIPPED, safety_critical=True),
    ]
    summary = summarize_session(state, mood_label="Stable")
    assert summary["total_tasks"] == 2
    assert summary["completed_tasks"] == 1
    assert summary["skipped_tasks"] == 1
    assert summary["completion_rate"] == 50.0
