"""Small LangChain adapter for an OpenAI-compatible chat endpoint.

Prompts and hidden reasoning are intentionally never returned to the logger.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import Settings
from .observability import StructuredJSONLLogger


@dataclass(frozen=True)
class ModelResult:
    value: dict[str, Any]
    input_tokens: int = 0
    output_tokens: int = 0
    used_fallback: bool = False
    usage_estimated: bool = False

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def _json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object, accepting a single fenced response."""
    value = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.DOTALL)
    if fenced:
        value = fenced.group(1)
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("model response must be a JSON object")
    return parsed


class JSONModelClient:
    """Bounded JSON calls with deterministic fallback for demo reliability."""

    def __init__(self, settings: Settings, logger: StructuredJSONLLogger) -> None:
        self.settings = settings
        self.logger = logger
        self._client: ChatOpenAI | None = None

    def _chat(self) -> ChatOpenAI:
        if self._client is None:
            self._client = ChatOpenAI(
                model=self.settings.openai_model,
                base_url=self.settings.openai_base_url,
                api_key=self.settings.openai_api_key or "local",
                max_tokens=self.settings.max_output_tokens_per_call,
                max_retries=0,
                timeout=self.settings.per_tool_timeout_seconds,
                use_responses_api=False,
            )
        return self._client

    def invoke(
        self,
        *,
        actor: str,
        system: str,
        payload: dict[str, Any],
        fallback: Callable[[], dict[str, Any]],
    ) -> ModelResult:
        if self.settings.offline:
            self.logger.event(
                actor=actor,
                event_type="model",
                status="FALLBACK",
                details={"reason": "offline", "model": self.settings.openai_model},
            )
            return ModelResult(fallback(), used_fallback=True)

        try:
            response = self._chat().invoke(
                [
                    SystemMessage(content=system),
                    HumanMessage(content=json.dumps(payload, ensure_ascii=False)),
                ]
            )
            content = response.content
            if not isinstance(content, str):
                raise ValueError("model returned non-text content")
            usage = response.usage_metadata or {}
            input_tokens = int(usage.get("input_tokens", 0) or 0)
            output_tokens = int(usage.get("output_tokens", 0) or 0)
            usage_estimated = not (input_tokens or output_tokens)
            if usage_estimated:
                input_tokens = max(
                    1,
                    (len(system) + len(json.dumps(payload, ensure_ascii=False)) + 3) // 4,
                )
                output_tokens = max(1, (len(content) + 3) // 4)
            result = ModelResult(
                value=_json_object(content),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                usage_estimated=usage_estimated,
            )
            self.logger.event(
                actor=actor,
                event_type="model",
                status="OK",
                details={
                    "model": self.settings.openai_model,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "usage_estimated": result.usage_estimated,
                },
            )
            return result
        except Exception as exc:
            if not self.settings.allow_model_fallback:
                raise
            self.logger.event(
                actor=actor,
                event_type="model",
                status="FALLBACK",
                details={"error_type": type(exc).__name__, "reason": "model_call_failed"},
            )
            return ModelResult(fallback(), used_fallback=True)
