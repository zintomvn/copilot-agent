from __future__ import annotations

import pytest
from pydantic import ValidationError

from aabw_agent.config import Settings
from aabw_agent.schemas import (
    CrossReference,
    DefectCase,
    EvidenceItem,
    ExecutionLimits,
    FinalState,
    ReviewPackage,
)


def test_settings_enforce_hard_turn_and_graph_caps() -> None:
    settings = Settings(max_turns=10_000, max_graph_steps=10_000)

    assert settings.max_turns == 40
    assert settings.max_graph_steps == 40


@pytest.mark.parametrize(
    "field",
    [
        "max_retrieval_loops",
        "max_tool_calls",
        "max_model_calls",
        "max_total_tokens",
        "max_output_tokens_per_call",
    ],
)
def test_settings_reject_non_positive_budgets(field: str) -> None:
    with pytest.raises(ValidationError, match="budget must be positive"):
        Settings(**{field: 0})


def test_execution_limit_defaults_stay_bounded() -> None:
    limits = ExecutionLimits()

    assert limits.max_graph_steps < 40
    assert limits.max_retrieval_loops <= 3
    assert limits.max_tool_calls == 30


def test_ingestion_to_workflow_contract_round_trip() -> None:
    payload = {
        "case_id": "CASE-INGEST-001",
        "aircraft_type": "A320",
        "defect_description": "Intermittent landing gear green indication.",
        "configuration": {"profile": "SYN-CFG-LG-A"},
        "entered_references": ["SYN-MEL-CURRENT"],
        "synthetic": True,
    }

    case = DefectCase.model_validate(payload)

    assert case.model_dump(mode="json")["configuration"] == {"profile": "SYN-CFG-LG-A"}
    assert case.entered_references == ["SYN-MEL-CURRENT"]


def test_evidence_and_cross_reference_enums_are_validated() -> None:
    evidence = EvidenceItem(
        evidence_id="EV-1",
        document_id="DOC-1",
        document_type="MEL",
        reference_number="REF-1",
        revision_id="R1",
        section_id="32-01",
        page_or_location="page 1",
        quoted_span="Synthetic evidence.",
        source_authority="AUTHORITATIVE",
        applicability_status="PASS",
        revision_status="CURRENT",
        approval_status="APPROVED",
        source_hash="sha256:test",
    )
    xref = CrossReference(
        from_evidence_id=evidence.evidence_id,
        reference_type="AMM_TASK",
        target_reference="REF-2",
        mandatory=True,
    )

    assert evidence.revision_status == "CURRENT"
    assert xref.status == "UNRESOLVED"
    with pytest.raises(ValidationError):
        EvidenceItem.model_validate({**evidence.model_dump(), "approval_status": "MAYBE"})


def test_terminal_review_package_requires_human_authority_notice() -> None:
    with pytest.raises(ValidationError):
        ReviewPackage(
            case_id="CASE-1",
            run_id="RUN-1",
            final_state=FinalState.ABSTAINED,
            case_summary="Synthetic case",
            normalized_case={},
            source_snapshot_id="snapshot-1",
            workflow_version="test",
            langfuse_trace_id="trace-1",
        )
