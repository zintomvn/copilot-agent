from __future__ import annotations

from aabw_agent.corpus import SyntheticCorpus


def test_corpus_results_are_deep_copies() -> None:
    corpus = SyntheticCorpus()
    result = corpus.lookup_document("SYN-MEL-CURRENT")
    assert result is not None
    result["title"] = "mutated"
    result["cross_references"].clear()
    fresh = corpus.lookup_document("SYN-MEL-CURRENT")
    assert fresh is not None
    assert fresh["title"] != "mutated"
    assert fresh["cross_references"]


def test_graph_resolves_mandatory_reference() -> None:
    corpus = SyntheticCorpus()
    related = corpus.traverse_evidence_graph(
        "SYN-MEL-CURRENT", relation_types=["CROSS_REFERENCE"], depth=1
    )
    assert [item["reference_number"] for item in related] == ["SYN-AMM-LINKED-CHECK"]
