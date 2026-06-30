from __future__ import annotations

from app.graph.state import Activity


def _to_minutes(time_str: str) -> int:
    hour, minute = map(int, time_str.split(":"))
    return hour * 60 + minute


def _from_minutes(minutes: int) -> str:
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def resolve_schedule_conflicts(activities: list[Activity]) -> list[Activity]:
    """Simple deterministic planner: sort by time/priority and push overlapping tasks forward."""
    ordered = sorted(activities, key=lambda a: (_to_minutes(a.preferred_time), -a.priority))
    last_end = 0
    planned: list[Activity] = []

    for activity in ordered:
        start = max(_to_minutes(activity.preferred_time), last_end)
        if activity.safety_critical and start > _to_minutes(activity.preferred_time) + 30:
            start = _to_minutes(activity.preferred_time)
        activity.preferred_time = _from_minutes(start)
        last_end = start + activity.duration_minutes
        planned.append(activity)

    return planned


def flag_safety_warnings(activities: list[Activity]) -> list[str]:
    warnings = []
    medication = [a for a in activities if a.category == "medication"]
    meals = [a for a in activities if a.category == "meal"]
    if medication and meals:
        first_med = min(_to_minutes(a.preferred_time) for a in medication)
        first_meal = min(_to_minutes(a.preferred_time) for a in meals)
        if first_med < first_meal:
            warnings.append("Medication appears before meal; check patient-specific instruction.")
    return warnings
