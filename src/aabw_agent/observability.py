"""Local structured traces for deterministic flow inspection."""

from __future__ import annotations

import json
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import Settings

_SECRET_KEYS = {"api_key", "apikey", "authorization", "password", "secret", "raw_prompt"}
_SECRET_KEY_FRAGMENTS = ("api_key", "apikey", "authorization", "password", "secret", "token")


def _is_secret_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in _SECRET_KEYS or any(fragment in lowered for fragment in _SECRET_KEY_FRAGMENTS)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if _is_secret_key(str(key)) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class StructuredJSONLLogger:
    def __init__(
        self,
        *,
        log_dir: Path,
        run_id: str,
        case_id: str,
        correlation_id: str,
        trace_id: str,
    ) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        self.path = log_dir / f"{run_id}.jsonl"
        self.run_id = run_id
        self.case_id = case_id
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self._lock = threading.Lock()
        self._sequence = 0

    def event(
        self,
        *,
        actor: str,
        event_type: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            self._sequence += 1
            record = {
                "timestamp": datetime.now(UTC).isoformat(),
                "sequence": self._sequence,
                "run_id": self.run_id,
                "case_id": self.case_id,
                "correlation_id": self.correlation_id,
                "trace_id": self.trace_id,
                "actor": actor,
                "event_type": event_type,
                "status": status,
                "details": _redact(details or {}),
            }
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def get_logger(
    *, log_dir: Path, run_id: str, case_id: str, correlation_id: str, trace_id: str
) -> StructuredJSONLLogger:
    return StructuredJSONLLogger(
        log_dir=log_dir,
        run_id=run_id,
        case_id=case_id,
        correlation_id=correlation_id,
        trace_id=trace_id,
    )


class LangfuseTelemetry:
    """Optional Langfuse bridge for LangChain/Deep Agents traces and evaluator scores."""

    def __init__(self, settings: Settings, logger: StructuredJSONLLogger | None = None) -> None:
        self.settings = settings
        self.logger = logger
        self.enabled = bool(
            settings.enable_langfuse
            and settings.langfuse_public_key
            and settings.langfuse_secret_key
        )
        self._client: Any | None = None

    def _configure_env(self) -> None:
        if self.settings.langfuse_public_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = self.settings.langfuse_public_key
        if self.settings.langfuse_secret_key:
            os.environ["LANGFUSE_SECRET_KEY"] = self.settings.langfuse_secret_key
        if self.settings.langfuse_base_url:
            os.environ["LANGFUSE_BASE_URL"] = self.settings.langfuse_base_url

    def callback_handler(self) -> Any | None:
        if not self.enabled:
            return None
        try:
            self._configure_env()
            from langfuse.langchain import CallbackHandler

            return CallbackHandler()
        except Exception as exc:  # pragma: no cover - depends on optional runtime setup
            if self.logger:
                self.logger.event(
                    actor="langfuse",
                    event_type="telemetry",
                    status="DISABLED",
                    details={"error_type": type(exc).__name__},
                )
            return None

    def client(self) -> Any | None:
        if not self.enabled:
            return None
        if self._client is None:
            try:
                self._configure_env()
                from langfuse import get_client

                self._client = get_client()
            except Exception as exc:  # pragma: no cover - depends on external credentials
                if self.logger:
                    self.logger.event(
                        actor="langfuse",
                        event_type="telemetry",
                        status="DISABLED",
                        details={"error_type": type(exc).__name__},
                    )
                self.enabled = False
        return self._client

    def create_score(
        self,
        *,
        trace_id: str,
        name: str,
        value: float | str,
        data_type: str,
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        client = self.client()
        if client is None:
            return
        try:
            client.create_score(
                trace_id=trace_id,
                name=name,
                value=value,
                data_type=data_type,
                comment=comment,
                metadata=metadata,
                environment=self.settings.langfuse_environment,
            )
        except Exception as exc:  # pragma: no cover - network/client dependent
            if self.logger:
                self.logger.event(
                    actor="langfuse",
                    event_type="score",
                    status="ERROR",
                    details={"score": name, "error_type": type(exc).__name__},
                )

    def flush(self) -> None:
        client = self.client()
        if client is None:
            return
        try:
            client.flush()
        except Exception:  # pragma: no cover - flushing must never break workflow
            return
