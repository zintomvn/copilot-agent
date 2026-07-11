"""Local structured traces for deterministic flow inspection."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SECRET_KEYS = {"api_key", "apikey", "authorization", "password", "secret", "raw_prompt"}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in _SECRET_KEYS else _redact(item)
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
