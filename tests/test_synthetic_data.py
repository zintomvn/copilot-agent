from __future__ import annotations

from aabw_agent.corpus import SyntheticCorpus
from aabw_agent.synthetic_data import generate


def test_generated_benchmark_data_is_valid_and_covers_required_scenarios(tmp_path) -> None:
    corpus_path = tmp_path / "benchmark_corpus.json"
    cases_path = tmp_path / "benchmark_cases.jsonl"

    result = generate(corpus_path, cases_path)
    corpus = SyntheticCorpus(corpus_path)
    raw_cases = cases_path.read_text(encoding="utf-8")

    assert result["documents"] >= 10
    assert result["cases_count"] >= 10
    assert corpus.source_snapshot_id == result["source_snapshot_id"]
    for expected_state in [
        "REVIEW_READY",
        "NEEDS_CLARIFICATION",
        "ABSTAINED",
        "ESCALATED",
    ]:
        assert f'"expected_final_state": "{expected_state}"' in raw_cases
    for source_type in ["TSM", "CDL", "ENGINEERING_PROCEDURE", "HISTORICAL_RECORD"]:
        assert f'"document_type": "{source_type}"' in corpus_path.read_text(encoding="utf-8")
