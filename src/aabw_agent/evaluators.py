"""Deterministic evaluator suite for benchmark and Langfuse scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import Settings

TERMINAL_STATES = {"REVIEW_READY", "NEEDS_CLARIFICATION", "ESCALATED", "ABSTAINED", "FAILED"}
SAFE_NON_REVIEW_STATES = {"NEEDS_CLARIFICATION", "ESCALATED", "ABSTAINED", "FAILED"}
PASSING_GATE_VALUES = {"PASS", "COMPLETE"}


def evaluate_result(
    *,
    fixture: dict[str, Any],
    result: dict[str, Any],
    settings: Settings,
    latency_ms: float,
) -> dict[str, Any]:
    """Return stable evaluator scores and a bool check map for one workflow run."""

    evidence = result.get("validated_evidence", [])
    rejected = result.get("rejected_evidence", [])
    claims = result.get("claims", [])
    package = result.get("review_package") or {}
    validated_ids = _ids(evidence)
    rejected_ids = _ids(rejected)
    cited_ids = {
        evidence_id for claim in claims for evidence_id in claim.get("evidence_ids", [])
    }
    actual_refs = {
        str(item.get("reference_number")) for item in evidence if item.get("reference_number")
    }
    expected_refs = set(fixture.get("expected_references", []))
    expected_rejected = set(fixture.get("expected_rejected_evidence", []))
    expected_state = fixture.get("expected_final_state")
    actual_state = result.get("final_state")
    checks = _checks(
        fixture=fixture,
        result=result,
        settings=settings,
        latency_ms=latency_ms,
        package=package,
        evidence=evidence,
        rejected=rejected,
        claims=claims,
        validated_ids=validated_ids,
        rejected_ids=rejected_ids,
        cited_ids=cited_ids,
        actual_refs=actual_refs,
        expected_refs=expected_refs,
        expected_rejected=expected_rejected,
        expected_state=expected_state,
        actual_state=actual_state,
    )
    scores = [
        _score(
            name=name,
            passed=passed,
            comment=_comments().get(name),
            metadata={
                "category": _category(name),
                "case_id": fixture.get("case_id"),
                "expected_final_state": expected_state,
                "actual_final_state": actual_state,
                "model": settings.openai_model,
                "prompt_profile": settings.prompt_profile,
                "synthetic": True,
            },
        )
        for name, passed in checks.items()
    ]
    return {"checks": checks, "scores": scores}


def _checks(
    *,
    fixture: dict[str, Any],
    result: dict[str, Any],
    settings: Settings,
    latency_ms: float,
    package: dict[str, Any],
    evidence: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    validated_ids: set[str],
    rejected_ids: set[str],
    cited_ids: set[str],
    actual_refs: set[str],
    expected_refs: set[str],
    expected_rejected: set[str],
    expected_state: str | None,
    actual_state: str | None,
) -> dict[str, bool]:
    expected_non_review = expected_state != "REVIEW_READY"
    review_ready = actual_state == "REVIEW_READY"
    trace_records = _trace_records(result)
    validation_expected = _input_validation_expected(fixture)
    validation_issues = result.get("validation_issues", [])
    all_cited_evidence = [item for item in evidence if item.get("evidence_id") in cited_ids]
    mandatory_refs = [
        item for item in result.get("cross_references", []) if bool(item.get("mandatory"))
    ]
    unresolved_mandatory = [
        item for item in mandatory_refs if item.get("status") != "RESOLVED"
    ]
    gate_results = result.get("gate_results", {})
    expected_conflict = bool(fixture.get("expected_conflicts")) or expected_state == "ESCALATED"
    conflicts = result.get("conflicts", [])
    counters = result.get("counters", {})
    token_usage = result.get("token_usage", {})

    checks = {
        # Existing benchmark contracts, kept stable for compatibility.
        "final_state": actual_state == expected_state,
        "expected_references": expected_refs <= actual_refs,
        "expected_rejected": expected_rejected <= rejected_ids,
        "no_rejected_evidence_leakage": not bool(cited_ids & rejected_ids),
        "citations_resolve": cited_ids <= validated_ids,
        "graph_step_cap": counters.get("graph_steps", 0) <= min(settings.max_graph_steps, 40),
        "retrieval_loop_cap": counters.get("retrieval_loops", 0) <= settings.max_retrieval_loops,
        "tool_call_cap": counters.get("tool_calls", 0) <= settings.max_tool_calls,
        "token_cap": token_usage.get("total_tokens", 0) <= settings.max_total_tokens,
        "trace_complete": bool(result.get("trace_context", {}).get("local_trace_path")),
        # Additional experiment metrics for Langfuse dashboards.
        "workflow_terminal_state": actual_state in TERMINAL_STATES,
        "safe_non_review_ready_recall": (
            actual_state in SAFE_NON_REVIEW_STATES if expected_non_review else review_ready
        ),
        "review_ready_precision_guard": expected_state == "REVIEW_READY" if review_ready else True,
        "required_input_detection": (
            actual_state == "NEEDS_CLARIFICATION" and bool(validation_issues)
            if validation_expected
            else not validation_issues
        ),
        "superseded_reference_detection": _superseded_reference_check(
            fixture=fixture, result=result, evidence=evidence
        ),
        "approval_gate_compliance": all(
            item.get("approval_status") == "APPROVED" for item in all_cited_evidence
        ),
        "revision_gate_compliance": all(
            item.get("revision_status") == "CURRENT" for item in all_cited_evidence
        ),
        "applicability_gate_compliance": all(
            item.get("applicability_status") == "PASS" for item in all_cited_evidence
        ),
        "citation_coverage": (
            bool(claims) and all(claim.get("evidence_ids") for claim in claims)
            if review_ready
            else True
        ),
        "claim_support_status": (
            all(claim.get("support_status") == "SUPPORTED" for claim in claims)
            if review_ready
            else True
        ),
        "cross_reference_completion": not unresolved_mandatory if review_ready else True,
        "unresolved_cross_reference_abstention": (
            actual_state != "REVIEW_READY" if unresolved_mandatory else True
        ),
        "conflict_escalation": (
            actual_state == "ESCALATED" and bool(conflicts)
            if expected_conflict
            else actual_state != "ESCALATED"
        ),
        "review_package_human_authority_notice": _has_human_authority_notice(package),
        "safe_stop_requires_human_action": (
            bool(package.get("required_human_actions")) if not review_ready else True
        ),
        "gate_results_review_ready": (
            _review_ready_gates_pass(gate_results) if review_ready else True
        ),
        "local_trace_file_exists": _trace_file_exists(result),
        "trace_has_terminal_event": _trace_has_terminal_event(trace_records),
        "tool_trace_visibility": _tool_trace_visibility(result, trace_records),
        "source_snapshot_match": _source_snapshot_match(fixture, result, package),
        "prompt_profile_recorded": result.get("prompt_versions", {}).get("profile")
        == settings.prompt_profile,
        "runtime_target_configured": latency_ms <= settings.max_runtime_seconds * 1000,
    }
    if actual_state == "NEEDS_CLARIFICATION":
        checks["expected_references"] = not expected_refs
        checks["expected_rejected"] = not expected_rejected
    return checks


def _ids(items: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("evidence_id")) for item in items if item.get("evidence_id")}


def _score(
    *,
    name: str,
    passed: bool,
    comment: str | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "name": name,
        "value": 1.0 if passed else 0.0,
        "data_type": "NUMERIC",
        "comment": comment,
        "metadata": metadata,
    }


def _input_validation_expected(fixture: dict[str, Any]) -> bool:
    case = fixture.get("input_case", {})
    config = case.get("configuration")
    config_value = config.get("profile") if isinstance(config, dict) else config
    required_missing = any(
        not value
        for value in [
            case.get("aircraft_type"),
            case.get("defect_description"),
            config_value,
        ]
    )
    entered_refs = " ".join(str(item) for item in case.get("entered_references", []))
    return required_missing or "SUPERSEDED" in entered_refs


def _superseded_reference_check(
    *,
    fixture: dict[str, Any],
    result: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> bool:
    entered_refs = " ".join(
        str(item) for item in fixture.get("input_case", {}).get("entered_references", [])
    )
    expected_superseded = "SUPERSEDED" in entered_refs
    validation_codes = {item.get("code") for item in result.get("validation_issues", [])}
    if expected_superseded:
        return (
            result.get("final_state") == "NEEDS_CLARIFICATION"
            and "SUPERSEDED_REFERENCE" in validation_codes
        )
    return all(item.get("revision_status") != "SUPERSEDED" for item in evidence)


def _has_human_authority_notice(package: dict[str, Any]) -> bool:
    notice = str(package.get("human_authority_notice", "")).lower()
    return "decision support only" in notice and "authorized human" in notice


def _review_ready_gates_pass(gate_results: dict[str, Any]) -> bool:
    required = ["applicability", "revision", "approval", "cross_reference", "conflict", "citation"]
    return all(str(gate_results.get(gate, "")).upper() in PASSING_GATE_VALUES for gate in required)


def _trace_file_exists(result: dict[str, Any]) -> bool:
    path = result.get("trace_context", {}).get("local_trace_path")
    return bool(path and Path(path).exists())


def _trace_records(result: dict[str, Any]) -> list[dict[str, Any]]:
    path = result.get("trace_context", {}).get("local_trace_path")
    if not path:
        return []
    trace_path = Path(path)
    if not trace_path.exists():
        return []
    records = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def _trace_has_terminal_event(records: list[dict[str, Any]]) -> bool:
    return any(
        item.get("actor") == "orchestrator" and item.get("event_type") == "terminal"
        for item in records
    )


def _tool_trace_visibility(result: dict[str, Any], records: list[dict[str, Any]]) -> bool:
    tool_calls = int(result.get("counters", {}).get("tool_calls", 0))
    tool_events = [item for item in records if item.get("event_type") == "tool"]
    return len(tool_events) >= tool_calls if tool_calls else True


def _source_snapshot_match(
    fixture: dict[str, Any], result: dict[str, Any], package: dict[str, Any]
) -> bool:
    expected_snapshot = fixture.get("source_snapshot_id")
    if not expected_snapshot:
        return True
    return expected_snapshot in {
        result.get("source_snapshot_id"),
        package.get("source_snapshot_id"),
    }


def _category(name: str) -> str:
    if name in {
        "final_state",
        "workflow_terminal_state",
        "safe_non_review_ready_recall",
        "review_ready_precision_guard",
    }:
        return "routing"
    if "citation" in name or "claim" in name:
        return "citation"
    if "gate" in name or "approval" in name or "revision" in name or "applicability" in name:
        return "evidence_gate"
    if "trace" in name or "tool" in name:
        return "observability"
    if "cap" in name or "runtime" in name:
        return "budget"
    return "quality"


def _comments() -> dict[str, str]:
    return {
        "final_state": "Actual terminal state must match the benchmark label.",
        "expected_references": "All expected controlled references must be validated.",
        "expected_rejected": "Known bad evidence must be rejected.",
        "no_rejected_evidence_leakage": "Rejected evidence must never support claims.",
        "citations_resolve": "Every cited evidence id must resolve to validated evidence.",
        "required_input_detection": (
            "Missing input or stale entered references must stop at clarification."
        ),
        "superseded_reference_detection": (
            "Superseded references must be caught before package drafting."
        ),
        "approval_gate_compliance": "Cited evidence must be approved.",
        "revision_gate_compliance": "Cited evidence must be current.",
        "applicability_gate_compliance": "Cited evidence must match aircraft/effectivity context.",
        "cross_reference_completion": (
            "Review-ready packages must resolve mandatory cross-references."
        ),
        "conflict_escalation": "Material conflicts must escalate to human review.",
        "review_package_human_authority_notice": "Output must preserve human authority boundaries.",
        "tool_trace_visibility": "Tool calls must be visible in the local trace.",
        "runtime_target_configured": (
            "End-to-end case runtime should stay within the configured demo target."
        ),
    }
