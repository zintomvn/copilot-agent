"""Secret-safe environment checker for demo readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values

from .config import Settings

_BOOL_FIELDS = {
    "OFFLINE",
    "ALLOW_MODEL_FALLBACK",
    "ENABLE_DEEP_AGENT",
    "ENABLE_LANGFUSE",
    "ENABLE_LLM_JUDGE",
}
_TRUE_FALSE = {"1", "0", "true", "false", "yes", "no", "y", "n", "on", "off", ""}


def _looks_set(value: str | None) -> bool:
    return bool(
        value
        and value.strip()
        and "replace-me" not in value
        and "replace-with" not in value
    )


def inspect_env(path: Path, *, check_network: bool = False) -> dict[str, Any]:
    values = {key.upper(): value for key, value in dotenv_values(path).items()}
    settings = Settings()
    malformed_bool = [
        key
        for key in sorted(_BOOL_FIELDS)
        if key in values and str(values[key]).strip().lower() not in _TRUE_FALSE
    ]
    result: dict[str, Any] = {
        "env_file": str(path),
        "openai_base_url": settings.openai_base_url,
        "openai_model": settings.openai_model,
        "deep_agent_model": settings.deep_agent_model or settings.openai_model,
        "llm_judge_model": settings.llm_judge_model or settings.openai_model,
        "prompt_profile": settings.prompt_profile,
        "max_runtime_seconds": settings.max_runtime_seconds,
        "model_timeout_seconds": settings.model_timeout_seconds,
        "per_tool_timeout_seconds": settings.per_tool_timeout_seconds,
        "retrieval_top_k": settings.retrieval_top_k,
        "openai_api_key_present": _looks_set(values.get("OPENAI_API_KEY")),
        "langfuse_public_key_present": _looks_set(values.get("LANGFUSE_PUBLIC_KEY")),
        "langfuse_secret_key_present": _looks_set(values.get("LANGFUSE_SECRET_KEY")),
        "enable_deep_agent": settings.enable_deep_agent,
        "enable_langfuse": settings.enable_langfuse,
        "enable_llm_judge": settings.enable_llm_judge,
        "malformed_boolean_fields": malformed_bool,
        "secret_safe": True,
    }
    if check_network:
        try:
            response = requests.get(
                settings.openai_base_url.rstrip("/") + "/models",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                timeout=10,
            )
            result["openai_models_status"] = response.status_code
        except Exception as exc:
            result["openai_models_status"] = "ERROR"
            result["openai_models_error_type"] = type(exc).__name__
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check AABW demo environment without printing keys"
    )
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--check-network", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_env(args.env_file, check_network=args.check_network)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["malformed_boolean_fields"]))


if __name__ == "__main__":
    raise SystemExit(main())
