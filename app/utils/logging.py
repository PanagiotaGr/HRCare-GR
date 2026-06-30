from __future__ import annotations

from datetime import datetime
from pathlib import Path
from app.graph.state import GraphState


def save_session_log(state: GraphState, log_dir: str) -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = f"session_{state.patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out = path / filename
    out.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return out
