"""Environment-backed runtime configuration and hard execution bounds."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    openai_base_url: str = "http://localhost:20128/v1"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = "local"
    offline: bool = False
    allow_model_fallback: bool = True

    max_turns: int = 40
    max_graph_steps: int = 20
    max_retrieval_loops: int = 3
    max_tool_calls: int = 30
    max_model_calls: int = 12
    max_total_tokens: int = 30_000
    max_output_tokens_per_call: int = 1_200
    max_runtime_seconds: float = 30.0
    per_tool_timeout_seconds: float = 8.0
    retry_count_per_tool: int = 2
    max_parallel_retrieval_tasks: int = 6
    max_candidates_per_path: int = 20

    log_level: str = "INFO"
    log_dir: Path = Path("logs/runs")
    corpus_path: Path = Path("data/synthetic_corpus.json")
    workflow_version: str = "aabw-langgraph-1.0.0"
    prompt_versions: dict[str, str] = Field(
        default_factory=lambda: {"planner": "1.0.0", "critic": "1.0.0"}
    )

    @field_validator("max_turns", mode="after")
    @classmethod
    def hard_turn_cap(cls, value: int) -> int:
        return max(1, min(value, 40))

    @field_validator("max_graph_steps", mode="after")
    @classmethod
    def hard_graph_cap(cls, value: int) -> int:
        return max(1, min(value, 40))

    @field_validator(
        "max_retrieval_loops",
        "max_tool_calls",
        "max_model_calls",
        "max_total_tokens",
        "max_output_tokens_per_call",
        "max_parallel_retrieval_tasks",
        "max_candidates_per_path",
        mode="after",
    )
    @classmethod
    def positive_int(cls, value: int) -> int:
        if value < 1:
            raise ValueError("budget must be positive")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
