from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ACTIVITY_TEMPLATES_PATH = DATA_DIR / "activities" / "adl_activity_templates.json"
SCENARIOS_PATH = DATA_DIR / "scenarios" / "public_adl_scenarios.json"


def load_adl_templates() -> dict[str, Any]:
    return json.loads(ACTIVITY_TEMPLATES_PATH.read_text(encoding="utf-8"))


def load_adl_scenarios() -> list[dict[str, Any]]:
    payload = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    return payload["scenarios"]


def get_scenario_by_id(scenario_id: str) -> dict[str, Any] | None:
    for scenario in load_adl_scenarios():
        if scenario["id"] == scenario_id:
            return scenario
    return None
