from app.graph.state import Activity
from app.rules.activity_rules import resolve_schedule_conflicts


def test_planner_pushes_overlapping_noncritical_activity():
    activities = [
        Activity(id="a1", title="Meal", category="meal", preferred_time="08:00", duration_minutes=30),
        Activity(id="a2", title="Exercise", category="exercise", preferred_time="08:10", duration_minutes=20),
    ]
    planned = resolve_schedule_conflicts(activities)
    assert planned[1].preferred_time == "08:30"
