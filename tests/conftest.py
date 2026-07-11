from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from aabw_agent.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def load_eval_cases() -> dict[str, dict[str, Any]]:
    records = (
        json.loads(line)
        for line in (ROOT / "data" / "eval_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    return {record["case_id"]: record for record in records}


@pytest.fixture
def eval_cases() -> dict[str, dict[str, Any]]:
    return load_eval_cases()


@pytest.fixture
def offline_settings(tmp_path: Path) -> Settings:
    return Settings(
        offline=True,
        log_dir=tmp_path / "logs",
        corpus_path=ROOT / "data" / "synthetic_corpus.json",
        max_turns=40,
        max_graph_steps=39,
        max_retrieval_loops=3,
        max_tool_calls=30,
    )
