from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from aabw_agent.config import Settings
from aabw_agent.corpus import SyntheticCorpus
from aabw_agent.ingestion import ControlledSpan, SourceSnapshotManifest


def test_graph_steps_and_turns_are_hard_capped_at_40() -> None:
    settings = Settings(max_graph_steps=500, max_turns=500)
    assert settings.max_graph_steps == 40
    assert settings.max_turns == 40


def test_corpus_exposes_valid_ingestion_snapshot_manifest() -> None:
    corpus = SyntheticCorpus()
    manifest = corpus.snapshot_manifest
    assert manifest.source_snapshot_id == corpus.source_snapshot_id
    assert len(manifest.documents) == len(corpus.documents)
    assert manifest.snapshot_digest == SourceSnapshotManifest.digest_documents(manifest.documents)


def test_controlled_span_rejects_reversed_offsets() -> None:
    with pytest.raises(ValidationError):
        ControlledSpan(
            span_id="span-1",
            document_id="doc-1",
            revision_id="R1",
            section_id="S1",
            page_or_location="p1",
            text="synthetic",
            character_start=10,
            character_end=2,
        )


def test_snapshot_digest_detects_metadata_mutation() -> None:
    corpus = SyntheticCorpus()
    data = corpus.snapshot_manifest.model_dump()
    data["documents"][0]["revision_id"] = "MUTATED"
    data["created_at"] = datetime.now(UTC)
    with pytest.raises(ValidationError):
        SourceSnapshotManifest.model_validate(data)
