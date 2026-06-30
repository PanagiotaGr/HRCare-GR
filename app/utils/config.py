from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    language: str = "el"
    llm_provider: str = "mock"
    log_dir: str = "experiments/logs"


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        language=os.getenv("HRC_LANGUAGE", "el"),
        llm_provider=os.getenv("HRC_LLM_PROVIDER", "mock"),
        log_dir=os.getenv("HRC_LOG_DIR", "experiments/logs"),
    )
