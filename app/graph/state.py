from __future__ import annotations

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class ActivityStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"


class Activity(BaseModel):
    id: str
    title: str
    category: Literal["medication", "meal", "exercise", "hydration", "social", "monitoring"]
    preferred_time: str
    duration_minutes: int = 15
    priority: int = Field(default=3, ge=1, le=5)
    safety_critical: bool = False
    status: ActivityStatus = ActivityStatus.PENDING
    notes: str = ""


class PatientProfile(BaseModel):
    patient_id: str
    name: str
    age: int
    language: str = "el"
    conditions: list[str]
    preferences: list[str]
    constraints: list[str]


class InteractionTurn(BaseModel):
    speaker: Literal["robot", "patient", "system"]
    text: str


class GraphState(BaseModel):
    patient_id: str
    doctor_instructions: str = ""
    simulation_time: str = "08:00"
    patient: PatientProfile | None = None
    retrieved_notes: list[str] = Field(default_factory=list)
    memory_notes: list[str] = Field(default_factory=list)
    activities: list[Activity] = Field(default_factory=list)
    current_activity_id: str | None = None
    conversation: list[InteractionTurn] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
