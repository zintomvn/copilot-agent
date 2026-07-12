from __future__ import annotations

from pathlib import Path

from aabw_agent.config import Settings
from aabw_agent.evaluate import load_jsonl
from aabw_agent.evaluators import evaluate_result
from aabw_agent.workflow import WorkflowRunner


def test_evaluator_suite_emits_langfuse_ready_scores(tmp_path: Path) -> None:
    fixture = load_jsonl(Path("data/eval_cases.jsonl"))[0]
    settings = Settings(offline=True, log_dir=tmp_path)
    result = WorkflowRunner(settings=settings).run(
        fixture["input_case"], expected_final_state=fixture["expected_final_state"]
    )

    evaluation = evaluate_result(
        fixture=fixture,
        result=result,
        settings=settings,
        latency_ms=100.0,
    )

    assert evaluation["checks"]["final_state"] is True
    score_names = {score["name"] for score in evaluation["scores"]}
    for expected in {
        "approval_gate_compliance",
        "citation_coverage",
        "conflict_escalation",
        "review_package_human_authority_notice",
        "tool_trace_visibility",
    }:
        assert expected in score_names
    assert all(score["data_type"] == "NUMERIC" for score in evaluation["scores"])
