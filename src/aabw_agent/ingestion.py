"""Typed handoff from controlled ingestion into retrieval and LangGraph runs.

These contracts model the output of architecture sections 6-7. They do not implement
file parsing or indexing; they prevent an agent run from receiving unversioned evidence.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IngestionContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=True)


class DocumentType(StrEnum):
    AMM = "AMM"
    MEL = "MEL"
    CDL = "CDL"
    TSM = "TSM"
    ENGINEERING_PROCEDURE = "ENGINEERING_PROCEDURE"
    HISTORICAL_RECORD = "HISTORICAL_RECORD"
    OTHER = "OTHER"


class ManifestApproval(StrEnum):
    APPROVED = "APPROVED"
    UNVERIFIED = "UNVERIFIED"
    SUPERSEDED = "SUPERSEDED"
    DRAFT = "DRAFT"
    REJECTED = "REJECTED"


class GateStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    FLAGGED = "FLAGGED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SourceRegistration(IngestionContract):
    document_id: str
    document_type: DocumentType
    title: str
    reference_number: str
    revision_id: str
    revision_date: date | None = None
    supersedes_revision: str | None = None
    approval_status: ManifestApproval
    effectivity: dict[str, Any] | None = None
    aircraft_types: tuple[str, ...] = ()
    configurations: tuple[str, ...] = ()
    source_repository: str
    source_uri: str | None = None
    synthetic: bool
    allow_listed: bool
    acl_tags: tuple[str, ...] = ()
    registered_by: str
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ImmutableRawArtifact(IngestionContract):
    document_id: str
    revision_id: str
    content_hash: str = Field(min_length=8)
    storage_version_id: str
    storage_uri: str
    media_type: str
    byte_length: int = Field(ge=0)
    uploaded_by: str
    uploaded_at: datetime


class ControlledSpan(IngestionContract):
    span_id: str
    document_id: str
    revision_id: str
    section_id: str
    page_or_location: str
    text: str
    heading_path: tuple[str, ...] = ()
    character_start: int | None = Field(default=None, ge=0)
    character_end: int | None = Field(default=None, ge=0)
    bounding_regions: tuple[dict[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    cautions: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    extracted_references: tuple[dict[str, Any], ...] = ()

    @model_validator(mode="after")
    def valid_offsets(self) -> ControlledSpan:
        if (
            self.character_start is not None
            and self.character_end is not None
            and self.character_end < self.character_start
        ):
            raise ValueError("character_end must not precede character_start")
        return self


class IngestionQualityGate(IngestionContract):
    source_allow_list: GateStatus
    manifest_schema: GateStatus
    content_hash: GateStatus
    revision_chain: GateStatus
    approval_metadata: GateStatus
    source_locations: GateStatus
    prompt_injection_scan: GateStatus
    cross_reference_schema: GateStatus
    synthetic_label: GateStatus
    issues: tuple[dict[str, Any], ...] = ()

    @property
    def publishable(self) -> bool:
        blocking = (
            self.source_allow_list,
            self.manifest_schema,
            self.content_hash,
            self.revision_chain,
            self.source_locations,
            self.cross_reference_schema,
            self.synthetic_label,
        )
        return all(status == GateStatus.PASS for status in blocking)

    @property
    def approved_evidence(self) -> bool:
        return self.publishable and self.approval_metadata == GateStatus.PASS


class RetrievalIndexRecord(IngestionContract):
    index_record_id: str
    span_id: str
    document_id: str
    revision_id: str
    reference_number: str
    document_type: DocumentType
    ata_chapter: str | None = None
    bm25_text: str
    embedding_id: str | None = None
    aircraft_types: tuple[str, ...] = ()
    configurations: tuple[str, ...] = ()
    approval_status: ManifestApproval
    source_authority: str
    cross_reference_targets: tuple[str, ...] = ()
    content_hash: str


class SnapshotDocumentRef(IngestionContract):
    document_id: str
    revision_id: str
    content_hash: str
    approval_status: ManifestApproval
    index_record_ids: tuple[str, ...] = ()


class SourceSnapshotManifest(IngestionContract):
    source_snapshot_id: str
    snapshot_digest: str
    corpus_id: str
    schema_version: str
    created_at: datetime
    synthetic: bool
    documents: tuple[SnapshotDocumentRef, ...]
    registry_version: str
    retrieval_config_version: str

    @staticmethod
    def digest_documents(documents: tuple[SnapshotDocumentRef, ...]) -> str:
        rows = sorted(
            (
                item.document_id,
                item.revision_id,
                item.content_hash,
                str(item.approval_status),
            )
            for item in documents
        )
        encoded = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    @model_validator(mode="after")
    def valid_digest_and_uniqueness(self) -> SourceSnapshotManifest:
        identities = {(item.document_id, item.revision_id) for item in self.documents}
        if len(identities) != len(self.documents):
            raise ValueError("snapshot contains duplicate document revision")
        expected = self.digest_documents(self.documents)
        if self.snapshot_digest != expected:
            raise ValueError("snapshot_digest does not match pinned document metadata")
        return self

    @classmethod
    def from_documents(
        cls,
        *,
        source_snapshot_id: str,
        corpus_id: str,
        schema_version: str,
        documents: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        synthetic: bool,
        registry_version: str = "synthetic-registry-v1",
        retrieval_config_version: str = "hybrid-v1",
    ) -> SourceSnapshotManifest:
        refs = tuple(
            SnapshotDocumentRef(
                document_id=item["document_id"],
                revision_id=item["revision_id"],
                content_hash=item["source_hash"],
                approval_status=item["approval_status"],
                index_record_ids=(item["evidence_id"],),
            )
            for item in documents
        )
        return cls(
            source_snapshot_id=source_snapshot_id,
            snapshot_digest=cls.digest_documents(refs),
            corpus_id=corpus_id,
            schema_version=schema_version,
            created_at=datetime.now(UTC),
            synthetic=synthetic,
            documents=refs,
            registry_version=registry_version,
            retrieval_config_version=retrieval_config_version,
        )


class IngestionHandoff(IngestionContract):
    registrations: tuple[SourceRegistration, ...]
    raw_artifacts: tuple[ImmutableRawArtifact, ...]
    spans: tuple[ControlledSpan, ...]
    quality_results: dict[str, IngestionQualityGate]
    index_records: tuple[RetrievalIndexRecord, ...]
    snapshot: SourceSnapshotManifest

    @model_validator(mode="after")
    def all_index_records_are_pinned(self) -> IngestionHandoff:
        pinned = {(item.document_id, item.revision_id) for item in self.snapshot.documents}
        indexed = {(item.document_id, item.revision_id) for item in self.index_records}
        if not indexed <= pinned:
            raise ValueError("index record is not pinned by source snapshot")
        span_ids = {span.span_id for span in self.spans}
        if any(record.span_id not in span_ids for record in self.index_records):
            raise ValueError("index record points to missing controlled span")
        return self


def load_ingestion_handoff(path: str | Path) -> IngestionHandoff:
    return IngestionHandoff.model_validate_json(Path(path).read_text(encoding="utf-8"))


__all__ = [
    "ControlledSpan",
    "DocumentType",
    "ImmutableRawArtifact",
    "IngestionHandoff",
    "IngestionQualityGate",
    "ManifestApproval",
    "RetrievalIndexRecord",
    "SnapshotDocumentRef",
    "SourceRegistration",
    "SourceSnapshotManifest",
    "load_ingestion_handoff",
]
