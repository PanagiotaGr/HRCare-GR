"""Persistent patient memory utilities for HRCare-GR.

The memory store is intentionally simple and file-based so the MVP remains easy
to run in a university/research setting without a database service. Each patient
has one JSON document containing session summaries, completed tasks, skipped
tasks, warnings, and lightweight preferences inferred from interaction history.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.graph.state import ActivityStatus, GraphState


DEFAULT_MEMORY_DIR = Path("experiments") / "memory"


class PatientMemory(BaseModel):
    patient_id: str
    sessions: list[dict[str, Any]] = Field(default_factory=list)
    completed_tasks: list[str] = Field(default_factory=list)
    skipped_tasks: list[str] = Field(default_factory=list)
    safety_warnings: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)

    def summary_notes(self, max_sessions: int = 3) -> list[str]:
        notes: list[str] = []
        recent_sessions = self.sessions[-max_sessions:]
        for session in recent_sessions:
            notes.append(
                "Previous session "
                f"{session.get('session_id', 'unknown')}: "
                f"completed={len(session.get('completed_tasks', []))}, "
                f"skipped={len(session.get('skipped_tasks', []))}, "
                f"warnings={len(session.get('warnings', []))}."
            )
        if self.preferences:
            notes.append("Known patient preferences: " + "; ".join(self.preferences[-5:]))
        if self.skipped_tasks:
            notes.append("Recently skipped tasks: " + "; ".join(self.skipped_tasks[-5:]))
        return notes


def memory_path(patient_id: str, memory_dir: Path = DEFAULT_MEMORY_DIR) -> Path:
    return memory_dir / f"{patient_id}.json"


def load_patient_memory(patient_id: str, memory_dir: Path = DEFAULT_MEMORY_DIR) -> PatientMemory:
    path = memory_path(patient_id, memory_dir)
    if not path.exists():
        return PatientMemory(patient_id=patient_id)
    return PatientMemory(**json.loads(path.read_text(encoding="utf-8")))


def save_patient_memory(memory: PatientMemory, memory_dir: Path = DEFAULT_MEMORY_DIR) -> Path:
    memory_dir.mkdir(parents=True, exist_ok=True)
    path = memory_path(memory.patient_id, memory_dir)
    path.write_text(memory.model_dump_json(indent=2), encoding="utf-8")
    return path


def attach_memory_to_state(state: GraphState, memory_dir: Path = DEFAULT_MEMORY_DIR) -> GraphState:
    """Load persistent memory and add it to retrieved notes for planning/context."""

    memory = load_patient_memory(state.patient_id, memory_dir)
    state.memory_notes = memory.summary_notes()
    if state.memory_notes:
        state.retrieved_notes.extend(state.memory_notes)
    return state


def update_memory_from_state(state: GraphState, memory_dir: Path = DEFAULT_MEMORY_DIR) -> PatientMemory:
    """Append a compact session summary to the patient's memory file."""

    memory = load_patient_memory(state.patient_id, memory_dir)
    completed = [activity.title for activity in state.activities if activity.status == ActivityStatus.DONE]
    skipped = [activity.title for activity in state.activities if activity.status == ActivityStatus.SKIPPED]

    session = {
        "session_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "simulation_time": state.simulation_time,
        "completed_tasks": completed,
        "skipped_tasks": skipped,
        "warnings": list(state.warnings),
        "turn_count": len(state.conversation),
    }

    memory.sessions.append(session)
    memory.completed_tasks.extend(completed)
    memory.skipped_tasks.extend(skipped)
    memory.safety_warnings.extend(state.warnings)

    if state.patient is not None:
        for preference in state.patient.preferences:
            if preference not in memory.preferences:
                memory.preferences.append(preference)

    save_patient_memory(memory, memory_dir)
    return memory
