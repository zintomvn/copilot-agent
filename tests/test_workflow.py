from __future__ import annotations

import json
from pathlib import Path

from aabw_agent.config import Settings
from aabw_agent.evaluate import load_jsonl
from aabw_agent.workflow import WorkflowRunner

DATASET = Path("data/eval_cases.jsonl")


def _settings(tmp_path: Path) -> Settings:
    return Settings(offline=True, log_dir=tmp_path)


def test_two_demo_cases_route_to_expected_states(tmp_path: Path) -> None:
    fixtures = load_jsonl(DATASET)[:2]
    for fixture in fixtures:
        result = WorkflowRunner(settings=_settings(tmp_path)).run(fixture["input_case"])
        assert result["final_state"] == fixture["expected_final_state"]
        assert result["counters"]["graph_steps"] <= 40


def test_unresolved_reference_stops_at_bounded_abstention(tmp_path: Path) -> None:
    fixture = load_jsonl(DATASET)[2]
    settings = _settings(tmp_path)
    result = WorkflowRunner(settings=settings).run(fixture["input_case"])
    assert result["final_state"] == "ABSTAINED"
    assert result["counters"]["retrieval_loops"] == settings.max_retrieval_loops
    assert result["counters"]["graph_steps"] < 40
    assert result["counters"]["tool_calls"] <= settings.max_tool_calls


def test_log_shows_agent_order_and_contains_no_secrets(tmp_path: Path) -> None:
    fixture = load_jsonl(DATASET)[0]
    result = WorkflowRunner(settings=_settings(tmp_path)).run(fixture["input_case"])
    trace = Path(result["trace_context"]["local_trace_path"])
    records = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    actors = [record["actor"] for record in records]
    expected = [
        "intake_agent",
        "input_validator",
        "orchestrator",
        "query_expansion_agent",
        "revision_temporal_agent",
        "keyword_metadata_agent",
        "cross_reference_graph_agent",
        "historical_context_agent",
        "retrieval_weighting_agent",
        "fusion_rerank_agent",
        "evidence_gate_supervisor",
        "synthesis_agent",
        "independent_critic",
    ]
    cursor = -1
    for actor in expected:
        cursor = actors.index(actor, cursor + 1)
    text = trace.read_text(encoding="utf-8").lower()
    assert "api_key" not in text
    assert "authorization" not in text
    assert "chain_of_thought" not in text


def test_review_ready_claims_never_use_rejected_evidence(tmp_path: Path) -> None:
    fixture = load_jsonl(DATASET)[0]
    result = WorkflowRunner(settings=_settings(tmp_path)).run(fixture["input_case"])
    rejected = {item["evidence_id"] for item in result["rejected_evidence"]}
    cited = {evidence_id for claim in result["claims"] for evidence_id in claim["evidence_ids"]}
    assert not cited & rejected


def test_historical_retrieval_uses_configured_top_k(tmp_path: Path) -> None:
    fixture = load_jsonl(DATASET)[0]
    settings = _settings(tmp_path)
    runner = WorkflowRunner(settings=settings)
    observed: dict[str, int] = {}
    original = runner.corpus.search_historical_cases

    def capture_top_k(case_features: object, top_k: int = 0) -> list[dict[str, object]]:
        observed["top_k"] = top_k
        return original(case_features, top_k=top_k)

    runner.corpus.search_historical_cases = capture_top_k  # type: ignore[method-assign]
    runner.run(fixture["input_case"])

    assert observed["top_k"] == settings.retrieval_top_k
