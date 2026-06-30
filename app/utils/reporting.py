from __future__ import annotations

from app.graph.state import ActivityStatus, GraphState


def summarize_session(state: GraphState, mood_label: str = "Neutral") -> dict[str, object]:
    total = len(state.activities)
    done = sum(1 for a in state.activities if a.status == ActivityStatus.DONE)
    skipped = sum(1 for a in state.activities if a.status == ActivityStatus.SKIPPED)
    pending = sum(1 for a in state.activities if a.status in {ActivityStatus.PENDING, ActivityStatus.IN_PROGRESS})
    critical_total = sum(1 for a in state.activities if a.safety_critical)
    critical_done = sum(1 for a in state.activities if a.safety_critical and a.status == ActivityStatus.DONE)
    completion_rate = round((done / total) * 100, 1) if total else 0.0

    return {
        "total_tasks": total,
        "completed_tasks": done,
        "skipped_tasks": skipped,
        "pending_tasks": pending,
        "critical_total": critical_total,
        "critical_completed": critical_done,
        "completion_rate": completion_rate,
        "mood": mood_label,
        "warnings": len(state.warnings),
    }


def caregiver_recommendation(summary: dict[str, object]) -> str:
    if summary["skipped_tasks"]:
        return "Review skipped activities and check whether the patient needs support."
    if summary["mood"] == "Needs attention":
        return "Consider contacting the patient or caregiver for a wellbeing check."
    if summary["completion_rate"] == 100:
        return "Routine is progressing well. Continue monitoring normally."
    return "Continue routine monitoring."
