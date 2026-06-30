from __future__ import annotations

import json
from pathlib import Path
from app.graph.state import GraphState, PatientProfile


PATIENT_DIR = Path(__file__).resolve().parents[1] / "data" / "patients"
GUIDELINES_PATH = Path(__file__).resolve().parents[1] / "data" / "care_guidelines" / "basic_elderly_care.md"


def retrieve_knowledge(state: GraphState) -> GraphState:
    patient_path = PATIENT_DIR / f"{state.patient_id}.json"
    if not patient_path.exists():
        raise FileNotFoundError(f"Unknown patient ID: {state.patient_id}")

    patient = PatientProfile(**json.loads(patient_path.read_text(encoding="utf-8")))
    guidelines = GUIDELINES_PATH.read_text(encoding="utf-8")

    state.patient = patient
    state.retrieved_notes = [guidelines, *patient.constraints, *patient.preferences]
    return state
