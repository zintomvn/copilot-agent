"""Typed contracts shared by graph nodes, tools, logs, and evaluation."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="allow", use_enum_values=True)


class WorkflowState(StrEnum):
    DRAFT = "DRAFT"
    VALIDATING_INPUT = "VALIDATING_INPUT"
    PLANNING = "PLANNING"
    RETRIEVING = "RETRIEVING"
    CHECKING_EVIDENCE = "CHECKING_EVIDENCE"
    DRAFTING_PACKAGE = "DRAFTING_PACKAGE"
    CRITIC_REVIEW = "CRITIC_REVIEW"
    REVIEW_READY = "REVIEW_READY"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    ESCALATED = "ESCALATED"
    ABSTAINED = "ABSTAINED"
    FAILED = "FAILED"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"


class FinalState(StrEnum):
    REVIEW_READY = "REVIEW_READY"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    ESCALATED = "ESCALATED"
    ABSTAINED = "ABSTAINED"
    FAILED = "FAILED"


class DefectCase(Contract):
    case_id: str
    aircraft_type: str = ""
    defect_description: str = ""
    aircraft_registration: str | None = None
    fleet_or_variant: str | None = None
    configuration: dict[str, Any] | None = None
    ata_chapter: str | None = None
    reported_symptoms: list[str] = Field(default_factory=list)
    flight_phase_or_context: str | None = None
    entered_references: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    created_by: str | None = None
    synthetic: bool = True


class SearchTask(Contract):
    source_type: str
    objective: str
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    target_reference: str | None = None


class EvidenceItem(Contract):
    evidence_id: str
    document_id: str
    document_type: str
    reference_number: str
    revision_id: str
    section_id: str
    page_or_location: str
    quoted_span: str
    retrieval_scores: dict[str, float] = Field(default_factory=dict)
    source_authority: Literal["AUTHORITATIVE", "SUPPORTING", "HISTORICAL_CONTEXT"]
    applicability_status: Literal["PASS", "FAIL", "UNKNOWN"]
    revision_status: Literal["CURRENT", "SUPERSEDED", "UNKNOWN"]
    approval_status: Literal["APPROVED", "UNVERIFIED", "REJECTED"]
    supports_claim_ids: list[str] = Field(default_factory=list)
    source_hash: str


class CrossReference(Contract):
    from_evidence_id: str
    reference_type: str
    target_reference: str
    mandatory: bool = False
    status: Literal["RESOLVED", "UNRESOLVED", "NOT_IN_CORPUS"] = "UNRESOLVED"
    retrieval_attempts: int = 0
    resolved_evidence_id: str | None = None


class Claim(Contract):
    claim_id: str
    claim_text: str
    claim_type: Literal[
        "FACT", "INCONSISTENCY", "MISSING_INFORMATION", "RECOMMENDED_REFERENCE", "LIMITATION"
    ]
    evidence_ids: list[str] = Field(default_factory=list)
    support_status: Literal["SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONFLICTED"]
    validator_results: list[dict[str, Any]] = Field(default_factory=list)


class Conflict(Contract):
    conflict_id: str
    conflict_type: str
    evidence_ids: list[str] = Field(default_factory=list)
    description: str
    material: bool = False
    resolution_status: Literal["UNRESOLVED", "HUMAN_RESOLVED"] = "UNRESOLVED"
    human_resolution: str | None = None


class Counters(Contract):
    graph_steps: int = 0
    retrieval_loops: int = 0
    tool_calls: int = 0
    model_calls: int = 0
    critic_retries: int = 0


class TokenUsage(Contract):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ExecutionLimits(Contract):
    max_graph_steps: int = 20
    max_retrieval_loops: int = 3
    max_tool_calls: int = 30
    max_model_calls: int = 12
    max_total_tokens: int = 30_000
    max_runtime_seconds: float = 30.0


class TraceContext(Contract):
    langfuse_trace_id: str
    correlation_id: str
    local_trace_path: str | None = None


class ReviewPackage(Contract):
    case_id: str
    run_id: str
    final_state: FinalState
    case_summary: str
    normalized_case: dict[str, Any]
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[dict[str, Any]] = Field(default_factory=list)
    plan_summary: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    recommended_references: list[dict[str, Any]] = Field(default_factory=list)
    applicability_checks: list[dict[str, Any]] = Field(default_factory=list)
    revision_checks: list[dict[str, Any]] = Field(default_factory=list)
    approval_checks: list[dict[str, Any]] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    required_human_actions: list[str] = Field(default_factory=list)
    human_authority_notice: str
    source_snapshot_id: str
    workflow_version: str
    langfuse_trace_id: str
