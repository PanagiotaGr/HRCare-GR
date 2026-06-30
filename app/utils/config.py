from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    language: str = "el"
    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    log_dir: str = "experiments/logs"


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        language=os.getenv("HRC_LANGUAGE", "el"),
        llm_provider=os.getenv("HRC_LLM_PROVIDER", "mock").lower(),
        llm_model=os.getenv("HRC_LLM_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        log_dir=os.getenv("HRC_LOG_DIR", "experiments/logs"),
    )
