from __future__ import annotations

import json
from pathlib import Path

from aabw_agent.observability import StructuredJSONLLogger


def test_logger_redacts_nested_known_secret_fields(tmp_path: Path) -> None:
    logger = StructuredJSONLLogger(
        log_dir=tmp_path,
        run_id="run-1",
        case_id="case-1",
        correlation_id="corr-1",
        trace_id="trace-1",
    )
    logger.event(
        actor="orchestrator",
        event_type="security_test",
        status="OK",
        details={
            "api_key": "top-secret-key",
            "nested": {"authorization": "Bearer secret", "safe": "visible"},
            "items": [{"password": "secret-password"}],
        },
    )

    raw = logger.path.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert "top-secret-key" not in raw
    assert "Bearer secret" not in raw
    assert "secret-password" not in raw
    assert record["details"] == {
        "api_key": "[REDACTED]",
        "nested": {"authorization": "[REDACTED]", "safe": "visible"},
        "items": [{"password": "[REDACTED]"}],
    }
