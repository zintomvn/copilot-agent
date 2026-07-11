from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from aabw_agent.config import Settings
from aabw_agent.evaluate import evaluate_fixture
from aabw_agent.workflow import WorkflowRunner


@pytest.mark.parametrize(
    ("case_id", "expected_state"),
    [
        ("EVAL-READY-001", "REVIEW_READY"),
        ("EVAL-CLARIFY-001", "NEEDS_CLARIFICATION"),
    ],
)
def test_two_offline_demo_examples(
    case_id: str,
    expected_state: str,
    eval_cases: dict[str, dict[str, Any]],
    offline_settings: Settings,
) -> None:
    fixture = eval_cases[case_id]

    evaluation = evaluate_fixture(fixture, offline_settings)

    assert evaluation["passed"] is True
    assert evaluation["actual_final_state"] == expected_state
    assert all(evaluation["checks"].values())


def test_ready_case_passes_data_between_all_components(
    eval_cases: dict[str, dict[str, Any]], offline_settings: Settings
) -> None:
    result = WorkflowRunner(settings=offline_settings).run(
        eval_cases["EVAL-READY-001"]["input_case"]
    )

    candidate_ids = {item["evidence_id"] for item in result["retrieval_candidates"]}
    validated_ids = {item["evidence_id"] for item in result["validated_evidence"]}
    package_ids = {item["evidence_id"] for item in result["review_package"]["evidence"]}
    cited_ids = {
        evidence_id
        for claim in result["review_package"]["claims"]
        for evidence_id in claim["evidence_ids"]
    }

    assert result["normalized_case"]["case_id"] == "EVAL-READY-001"
    assert result["search_tasks"]
    assert validated_ids <= candidate_ids
    assert package_ids == validated_ids
    assert cited_ids <= package_ids
    assert result["gate_results"] == {
        "applicability": "PASS",
        "revision": "PASS",
        "approval": "PASS",
        "cross_reference": "COMPLETE",
        "conflict": "PASS",
        "citation": "PASS",
        "completeness": "PASS",
    }
    assert result["final_state"] == "REVIEW_READY"


def test_unresolved_cross_reference_stops_within_all_caps(
    eval_cases: dict[str, dict[str, Any]], offline_settings: Settings
) -> None:
    result = WorkflowRunner(settings=offline_settings).run(
        eval_cases["EVAL-UNRESOLVED-XREF-001"]["input_case"]
    )

    assert result["final_state"] == "ABSTAINED"
    assert result["counters"]["retrieval_loops"] == 3
    assert result["counters"]["retrieval_loops"] <= result["limits"]["max_retrieval_loops"]
    assert result["counters"]["graph_steps"] < 40
    assert result["counters"]["tool_calls"] <= result["limits"]["max_tool_calls"]
    assert all(reference["retrieval_attempts"] <= 3 for reference in result["cross_references"])
    assert any(
        reference["mandatory"] and reference["status"] == "NOT_IN_CORPUS"
        for reference in result["cross_references"]
    )


def test_low_tool_budget_abstains_without_exceeding_cap(
    tmp_path: Path, eval_cases: dict[str, dict[str, Any]]
) -> None:
    settings = Settings(
        offline=True,
        log_dir=tmp_path / "logs",
        max_tool_calls=2,
        max_graph_steps=39,
        max_turns=40,
    )

    result = WorkflowRunner(settings=settings).run(eval_cases["EVAL-READY-001"]["input_case"])

    assert result["final_state"] == "ABSTAINED"
    assert result["counters"]["tool_calls"] == 2
    assert result["counters"]["graph_steps"] < 40


def test_trace_records_ordered_agents_and_never_logs_secret(
    tmp_path: Path, eval_cases: dict[str, dict[str, Any]]
) -> None:
    secret = "TEST-API-KEY-MUST-NOT-APPEAR"
    settings = Settings(
        offline=True,
        openai_api_key=secret,
        log_dir=tmp_path / "logs",
        max_graph_steps=39,
    )
    result = WorkflowRunner(settings=settings).run(eval_cases["EVAL-READY-001"]["input_case"])
    trace_path = Path(result["trace_context"]["local_trace_path"])
    raw_trace = trace_path.read_text(encoding="utf-8")
    records = [json.loads(line) for line in raw_trace.splitlines()]

    assert secret not in raw_trace
    assert all(record["sequence"] == index for index, record in enumerate(records, start=1))
    node_actors = [record["actor"] for record in records if record["event_type"] == "node_start"]
    assert node_actors == [
        "intake_agent",
        "input_validator",
        "orchestrator",
        "retrieval_supervisor",
        "fusion_rerank_agent",
        "evidence_gate_supervisor",
        "synthesis_agent",
        "independent_critic",
    ]
    specialist_starts = [
        record["actor"]
        for record in records
        if record["event_type"] == "agent" and record["status"] == "START"
    ]
    assert specialist_starts == [
        "query_expansion_agent",
        "revision_temporal_agent",
        "keyword_metadata_agent",
        "cross_reference_graph_agent",
        "historical_context_agent",
    ]
    assert records[0]["actor"] == "orchestrator"
    assert records[0]["event_type"] == "run_start"
    assert records[-1]["actor"] == "orchestrator"
    assert records[-1]["event_type"] == "terminal"
