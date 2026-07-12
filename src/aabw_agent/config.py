"""Environment-backed runtime configuration and hard execution bounds."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    openai_base_url: str = "http://localhost:20128/v1"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = "local"
    offline: bool = False
    allow_model_fallback: bool = True
    enable_deep_agent: bool = True
    deep_agent_model: str | None = None
    llm_judge_model: str | None = None
    enable_llm_judge: bool = False
    prompt_profile: str = "safety_default"

    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str = "https://cloud.langfuse.com"
    enable_langfuse: bool = False
    langfuse_environment: str = "hackathon-demo"

    max_turns: int = 40
    max_graph_steps: int = 20
    max_retrieval_loops: int = 3
    max_tool_calls: int = 30
    max_model_calls: int = 12
    max_total_tokens: int = 30_000
    max_output_tokens_per_call: int = 1_200
    max_runtime_seconds: float = 90.0
    model_timeout_seconds: float = 60.0
    per_tool_timeout_seconds: float = 8.0
    retry_count_per_tool: int = 2
    max_parallel_retrieval_tasks: int = 6
    max_candidates_per_path: int = 20
    retrieval_top_k: int = 13

    log_level: str = "INFO"
    log_dir: Path = Path("logs/runs")
    corpus_path: Path = Path("data/synthetic_corpus.json")
    upload_dir: Path = Path("data/uploads")
    ingested_corpus_path: Path = Path("data/ingested_corpus.json")
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
    workflow_version: str = "aabw-langgraph-1.0.0"
    prompt_versions: dict[str, str] = Field(
        default_factory=lambda: {"planner": "1.0.0", "critic": "1.0.0"}
    )

    @field_validator(
        "offline",
        "allow_model_fallback",
        "enable_deep_agent",
        "enable_llm_judge",
        "enable_langfuse",
        mode="before",
    )
    @classmethod
    def tolerant_bool(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on"}:
                return True
            if normalized in {"0", "false", "no", "n", "off", ""}:
                return False
            # Prevent malformed .env secrets from crashing demo startup.
            if normalized.startswith(("sk-", "pk-", "sk_", "pk_")):
                return False
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str] | object:
        if value is None:
            return []
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            parsed: object
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parts = [item.strip().strip("\"'") for item in raw.strip("[]").split(",")]
                return [item for item in parts if item]
            value = parsed
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return value

    @field_validator("cors_origins", mode="after")
    @classmethod
    def ensure_local_dev_origins(cls, value: list[str]) -> list[str]:
        merged: list[str] = []
        for origin in [
            *(value or []),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]:
            if origin not in merged:
                merged.append(origin)
        return merged

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
        "retrieval_top_k",
        mode="after",
    )
    @classmethod
    def positive_int(cls, value: int) -> int:
        if value < 1:
            raise ValueError("budget must be positive")
        return value

    @field_validator(
        "max_runtime_seconds",
        "model_timeout_seconds",
        "per_tool_timeout_seconds",
        mode="after",
    )
    @classmethod
    def positive_float(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("timeout must be positive")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
