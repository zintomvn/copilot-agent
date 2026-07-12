"""Bounded LangGraph implementation of architecture sections 9 and 10."""

from __future__ import annotations

import copy
import time
import uuid
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .config import Settings, get_settings
from .corpus import SyntheticCorpus
from .deep_agent import DeepAgentHarness
from .llm import JSONModelClient, ModelResult
from .observability import LangfuseTelemetry, StructuredJSONLLogger, get_logger
from .schemas import (
    Claim,
    Counters,
    CrossReference,
    DefectCase,
    EvidenceItem,
    ExecutionLimits,
    FinalState,
    ReviewPackage,
    SearchTask,
    TokenUsage,
    TraceContext,
    WorkflowState,
)

HUMAN_AUTHORITY_NOTICE = (
    "Decision support only. An authorized human must open and verify the controlled source; "
    "this package does not authorize dispatch, airworthiness, certification, maintenance, or "
    "release to service."
)


class GraphState(TypedDict, total=False):
    run_id: str
    case_id: str
    workflow_version: str
    prompt_versions: dict[str, str]
    source_snapshot_id: str
    ingestion_snapshot: dict[str, Any]
    raw_input: dict[str, Any]
    normalized_case: dict[str, Any] | None
    validation_issues: list[dict[str, Any]]
    plan: list[dict[str, Any]]
    search_tasks: list[dict[str, Any]]
    retrieval_candidates: list[dict[str, Any]]
    validated_evidence: list[dict[str, Any]]
    rejected_evidence: list[dict[str, Any]]
    cross_references: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    review_package: dict[str, Any] | None
    critic_findings: list[dict[str, Any]]
    gate_results: dict[str, Any]
    workflow_state: str
    final_state: str | None
    human_review: dict[str, Any] | None
    counters: dict[str, int]
    token_usage: dict[str, int]
    limits: dict[str, Any]
    trace_context: dict[str, Any]
    route: str
    route_reason: str
    started_monotonic: float
    expected_final_state: str | None
    execution_warnings: list[str]


class BudgetExceeded(RuntimeError):
    pass


def _configuration_profile(case: dict[str, Any]) -> str | None:
    config = case.get("configuration")
    if isinstance(config, dict):
        value = config.get("profile") or config.get("id") or config.get("name")
        return str(value) if value else None
    return None


def _evidence_item(document: dict[str, Any]) -> dict[str, Any]:
    fields = EvidenceItem.model_fields
    payload = {key: document.get(key) for key in fields}
    payload["retrieval_scores"] = document.get("retrieval_scores", {})
    payload["supports_claim_ids"] = document.get("supports_claim_ids", [])
    return EvidenceItem.model_validate(payload).model_dump(mode="json")


class WorkflowRunner:
    """One runner per process; evaluation invokes cases sequentially for deterministic logs."""

    def __init__(
        self,
        settings: Settings | None = None,
        corpus: SyntheticCorpus | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.corpus = corpus or SyntheticCorpus(self.settings.corpus_path)
        self.logger: StructuredJSONLLogger | None = None
        self.model: JSONModelClient | None = None
        self.telemetry: LangfuseTelemetry | None = None
        self.deep_agent: DeepAgentHarness | None = None

    def _log(
        self, actor: str, event_type: str, status: str, details: dict[str, Any] | None = None
    ) -> None:
        assert self.logger is not None
        self.logger.event(actor=actor, event_type=event_type, status=status, details=details)

    def _enter(self, state: GraphState, actor: str, target: WorkflowState) -> GraphState:
        result = copy.deepcopy(state)
        counters = Counters.model_validate(result["counters"])
        limits = ExecutionLimits.model_validate(result["limits"])
        elapsed = time.monotonic() - result["started_monotonic"]
        if counters.graph_steps >= limits.max_graph_steps:
            return self._terminal(result, FinalState.ABSTAINED, "max_graph_steps exhausted")
        if elapsed >= limits.max_runtime_seconds:
            return self._terminal(result, FinalState.ABSTAINED, "max_runtime_seconds exhausted")
        before = result.get("workflow_state")
        counters.graph_steps += 1
        result["counters"] = counters.model_dump()
        result["workflow_state"] = target.value
        self._log(
            actor,
            "node_start",
            "OK",
            {
                "state_before": before,
                "state_after": target.value,
                "graph_steps": counters.graph_steps,
                "retrieval_loops": counters.retrieval_loops,
                "tool_calls": counters.tool_calls,
                "model_calls": counters.model_calls,
            },
        )
        return result

    def _finish(
        self, state: GraphState, actor: str, *, route: str, reason: str, output: Any = None
    ) -> GraphState:
        result = copy.deepcopy(state)
        result["route"] = route
        result["route_reason"] = reason
        summary: dict[str, Any] = {"route": route, "route_reason": reason}
        if isinstance(output, list):
            summary["output_count"] = len(output)
        elif isinstance(output, dict):
            summary["output_keys"] = sorted(output)
        self._log(actor, "node_end", "OK", summary)
        return result

    def _terminal(self, state: GraphState, final: FinalState, reason: str) -> GraphState:
        result = copy.deepcopy(state)
        result["final_state"] = final.value
        result["workflow_state"] = final.value
        result["route"] = "finalize"
        result["route_reason"] = reason
        self._log(
            "orchestrator",
            "transition",
            "SAFE_TERMINAL" if final != FinalState.REVIEW_READY else "OK",
            {"final_state": final.value, "reason": reason},
        )
        return result

    def _tool(self, state: GraphState, actor: str, name: str, call: Any) -> tuple[Any, GraphState]:
        result = copy.deepcopy(state)
        counters = Counters.model_validate(result["counters"])
        limits = ExecutionLimits.model_validate(result["limits"])
        if counters.tool_calls >= limits.max_tool_calls:
            raise BudgetExceeded("max_tool_calls exhausted")
        started = time.perf_counter()
        client = self.telemetry.client() if self.telemetry else None
        try:
            if client is not None:
                with client.start_as_current_observation(
                    as_type="span",
                    name=f"tool:{name}",
                ) as span:
                    span.update(
                        input={"actor": actor, "tool": name},
                        metadata={
                            "workflow_version": result["workflow_version"],
                            "case_id": result["case_id"],
                            "source_snapshot_id": result["source_snapshot_id"],
                        },
                    )
                    output = call()
                    span.update(
                        output={
                            "result_count": len(output)
                            if isinstance(output, list)
                            else int(output is not None)
                        }
                    )
            else:
                output = call()
        except Exception as exc:
            self._log(
                actor,
                "tool",
                "ERROR",
                {"tool": name, "error_type": type(exc).__name__},
            )
            raise
        counters.tool_calls += 1
        result["counters"] = counters.model_dump()
        self._log(
            actor,
            "tool",
            "OK",
            {
                "tool": name,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "result_count": len(output)
                if isinstance(output, list)
                else int(output is not None),
                "tool_calls": counters.tool_calls,
            },
        )
        return output, result

    def _model_call(
        self,
        state: GraphState,
        *,
        actor: str,
        system: str,
        payload: dict[str, Any],
        fallback: Any,
    ) -> tuple[ModelResult, GraphState]:
        result = copy.deepcopy(state)
        assert self.model is not None
        counters = Counters.model_validate(result["counters"])
        tokens = TokenUsage.model_validate(result["token_usage"])
        limits = ExecutionLimits.model_validate(result["limits"])
        if not self.settings.offline:
            if counters.model_calls >= limits.max_model_calls:
                raise BudgetExceeded("max_model_calls exhausted")
            if (
                tokens.total_tokens + self.settings.max_output_tokens_per_call
                > limits.max_total_tokens
            ):
                raise BudgetExceeded("max_total_tokens reservation exhausted")
        if (
            self.deep_agent is not None
            and actor in {"orchestrator", "independent_critic"}
            and self.settings.enable_deep_agent
        ):
            response = self.deep_agent.invoke(
                actor=actor,
                stage="planning" if actor == "orchestrator" else "critic",
                payload=payload,
                fallback=fallback,
                trace_id=result["trace_context"]["langfuse_trace_id"],
                correlation_id=result["trace_context"]["correlation_id"],
            )
        else:
            response = self.model.invoke(
                actor=actor, system=system, payload=payload, fallback=fallback
            )
        if response.used_fallback:
            result.setdefault("execution_warnings", []).append(
                f"{actor} used deterministic model fallback; "
                "inspect trace before relying on output."
            )
        if not self.settings.offline:
            counters.model_calls += 1
            tokens.input_tokens += response.input_tokens
            tokens.output_tokens += response.output_tokens
            tokens.total_tokens = tokens.input_tokens + tokens.output_tokens
        result["counters"] = counters.model_dump()
        result["token_usage"] = tokens.model_dump()
        return response, result

    def _normalize(self, state: GraphState) -> GraphState:
        result = self._enter(state, "intake_agent", WorkflowState.VALIDATING_INPUT)
        if result.get("final_state"):
            return result
        raw = copy.deepcopy(result["raw_input"])
        raw.setdefault("case_id", result["case_id"])
        raw.setdefault("synthetic", True)
        try:
            normalized = DefectCase.model_validate(raw)
        except Exception as exc:
            result["validation_issues"] = [
                {"field": "schema", "code": "INVALID", "message": str(exc)}
            ]
            return self._terminal(result, FinalState.NEEDS_CLARIFICATION, "input schema invalid")
        result["normalized_case"] = normalized.model_dump(mode="json")
        return self._finish(
            result,
            "intake_agent",
            route="validate",
            reason="language detected; schema normalized",
            output=result["normalized_case"],
        )

    def _validate(self, state: GraphState) -> GraphState:
        result = self._enter(state, "input_validator", WorkflowState.VALIDATING_INPUT)
        if result.get("final_state"):
            return result
        case = result.get("normalized_case") or {}
        issues: list[dict[str, Any]] = []
        required = {
            "aircraft_type": case.get("aircraft_type"),
            "defect_description": case.get("defect_description"),
            "configuration": _configuration_profile(case),
        }
        for field, value in required.items():
            if not value or (isinstance(value, str) and not value.strip()):
                issues.append({"field": field, "code": "REQUIRED", "message": "value required"})
        for reference in case.get("entered_references", []):
            document = self.corpus.lookup_document(reference)
            if not document:
                issues.append(
                    {
                        "field": "entered_references",
                        "code": "UNKNOWN_REFERENCE",
                        "message": f"reference {reference} not found in controlled registry",
                        "reference": reference,
                    }
                )
                continue
            if document.get("revision_status") == "SUPERSEDED":
                chain = self.corpus.get_revision_chain(document["document_id"])
                current = next(
                    (item for item in chain if item.get("revision_status") == "CURRENT"),
                    None,
                )
                issues.append(
                    {
                        "field": "entered_references",
                        "code": "SUPERSEDED_REFERENCE",
                        "message": f"reference {reference} is superseded",
                        "reference": reference,
                        "current_reference": current.get("reference_number") if current else None,
                    }
                )
        result["validation_issues"] = issues
        self._log(
            "input_validator",
            "gate",
            "FAIL" if issues else "PASS",
            {
                "gate": "required_field_and_reference",
                "issues": [
                    {"field": x["field"], "code": x["code"]} for x in issues
                ],
            },
        )
        if issues:
            return self._terminal(
                result,
                FinalState.NEEDS_CLARIFICATION,
                "critical input or entered reference requires clarification",
            )
        return self._finish(result, "input_validator", route="plan", reason="required fields pass")

    def _fallback_plan(self, case: dict[str, Any]) -> dict[str, Any]:
        query = case["defect_description"]
        filters = {
            "aircraft_type": case["aircraft_type"],
            "configuration": _configuration_profile(case),
            "ata_chapter": case.get("ata_chapter"),
        }
        tasks = [
            SearchTask(
                source_type="AMM",
                objective="locate maintenance reference",
                query=query,
                filters=filters,
            ),
            SearchTask(
                source_type="MEL",
                objective="validate entered reference",
                query=query,
                filters=filters,
            ),
            SearchTask(
                source_type="TSM", objective="locate symptom evidence", query=query, filters=filters
            ),
            SearchTask(
                source_type="CDL",
                objective="check configuration deviation references when relevant",
                query=query,
                filters=filters,
            ),
            SearchTask(
                source_type="ENGINEERING_PROCEDURE",
                objective="check controlled engineering procedure context when relevant",
                query=query,
                filters=filters,
            ),
        ]
        return {
            "plan": [
                "validate exact references and revisions",
                "retrieve controlled synthetic evidence through specialist paths",
                "apply deterministic gates and resolve mandatory references",
                "draft cited package and run independent critic",
            ],
            "search_tasks": [task.model_dump(mode="json") for task in tasks],
        }

    def _plan(self, state: GraphState) -> GraphState:
        result = self._enter(state, "orchestrator", WorkflowState.PLANNING)
        if result.get("final_state"):
            return result
        case = result["normalized_case"] or {}

        def fallback() -> dict[str, Any]:
            return self._fallback_plan(case)

        try:
            response, result = self._model_call(
                result,
                actor="orchestrator",
                system=(
                    "Create a short bounded evidence-retrieval plan. Return JSON object with plan "
                    "(array of strings) and search_tasks (array). Never provide maintenance steps, "
                    "dispatch advice, hidden reasoning, or authority decisions."
                ),
                payload={
                    "case": case,
                    "allowed_sources": [
                        "AMM",
                        "MEL",
                        "CDL",
                        "TSM",
                        "ENGINEERING_PROCEDURE",
                        "HISTORICAL_RECORD",
                    ],
                    "max_retrieval_loops": result["limits"]["max_retrieval_loops"],
                    "source_snapshot_id": result["source_snapshot_id"],
                    "workflow_version": result["workflow_version"],
                },
                fallback=fallback,
            )
            plan_data = response.value
            if not isinstance(plan_data.get("plan"), list) or not isinstance(
                plan_data.get("search_tasks"), list
            ):
                plan_data = fallback()
        except BudgetExceeded as exc:
            return self._terminal(result, FinalState.ABSTAINED, str(exc))
        result["plan"] = [
            {"step": str(item), "bounded": True} for item in plan_data.get("plan", [])[:8]
        ]
        fallback_tasks = fallback()["search_tasks"]
        try:
            tasks = [
                SearchTask.model_validate(item).model_dump(mode="json")
                for item in plan_data["search_tasks"][:6]
            ]
        except Exception:
            tasks = fallback_tasks
        if not tasks:
            tasks = fallback_tasks
        result["search_tasks"] = tasks
        return self._finish(
            result, "orchestrator", route="retrieve", reason="bounded plan ready", output=tasks
        )

    def _retrieval_team(self, state: GraphState) -> GraphState:
        result = self._enter(state, "retrieval_supervisor", WorkflowState.RETRIEVING)
        if result.get("final_state"):
            return result
        counters = Counters.model_validate(result["counters"])
        limits = ExecutionLimits.model_validate(result["limits"])
        if counters.retrieval_loops >= limits.max_retrieval_loops:
            return self._terminal(result, FinalState.ABSTAINED, "max_retrieval_loops exhausted")
        counters.retrieval_loops += 1
        result["counters"] = counters.model_dump()
        case = result["normalized_case"] or {}
        filters = {
            "aircraft_type": case.get("aircraft_type"),
            "ata_chapter": case.get("ata_chapter"),
        }
        query = case.get("defect_description", "")
        top_k = min(self.settings.retrieval_top_k, self.settings.max_candidates_per_path)
        candidates: list[dict[str, Any]] = []
        try:
            self._log("query_expansion_agent", "agent", "START", {"loop": counters.retrieval_loops})
            found, result = self._tool(
                result,
                "query_expansion_agent",
                "search_semantic",
                lambda: self.corpus.search_semantic(query, filters=filters, top_k=top_k),
            )
            candidates.extend(found)
            self._log("query_expansion_agent", "agent", "END", {"output_count": len(found)})

            self._log(
                "revision_temporal_agent", "agent", "START", {"loop": counters.retrieval_loops}
            )
            revision_found: list[dict[str, Any]] = []
            for reference in case.get("entered_references", []):
                doc, result = self._tool(
                    result,
                    "revision_temporal_agent",
                    "lookup_document",
                    lambda ref=reference: self.corpus.lookup_document(ref),
                )
                if doc:
                    doc = copy.deepcopy(doc)
                    doc.setdefault("retrieval_scores", {})["exact"] = 1.0
                    revision_found.append(doc)
            candidates.extend(revision_found)
            self._log(
                "revision_temporal_agent", "agent", "END", {"output_count": len(revision_found)}
            )

            self._log(
                "keyword_metadata_agent", "agent", "START", {"loop": counters.retrieval_loops}
            )
            lexical, result = self._tool(
                result,
                "keyword_metadata_agent",
                "search_lexical",
                lambda: self.corpus.search_lexical(query, filters=filters, top_k=top_k),
            )
            candidates.extend(lexical)
            self._log("keyword_metadata_agent", "agent", "END", {"output_count": len(lexical)})

            self._log(
                "cross_reference_graph_agent", "agent", "START", {"loop": counters.retrieval_loops}
            )
            graph_found: list[dict[str, Any]] = []
            for doc in revision_found:
                related, result = self._tool(
                    result,
                    "cross_reference_graph_agent",
                    "traverse_evidence_graph",
                    lambda doc_id=doc["document_id"]: self.corpus.traverse_evidence_graph(
                        doc_id, depth=1
                    ),
                )
                graph_found.extend(related)
            candidates.extend(graph_found)
            self._log(
                "cross_reference_graph_agent", "agent", "END", {"output_count": len(graph_found)}
            )

            self._log(
                "historical_context_agent", "agent", "START", {"loop": counters.retrieval_loops}
            )
            history, result = self._tool(
                result,
                "historical_context_agent",
                "search_historical_cases",
                lambda: self.corpus.search_historical_cases(case, top_k=top_k),
            )
            candidates.extend(history)
            self._log("historical_context_agent", "agent", "END", {"output_count": len(history)})

            self._log(
                "retrieval_weighting_agent",
                "agent",
                "END",
                {"weights": {"semantic": 0.35, "lexical": 0.25, "exact": 0.25, "graph": 0.15}},
            )
        except BudgetExceeded as exc:
            return self._terminal(result, FinalState.ABSTAINED, str(exc))
        except Exception as exc:
            self._log("retrieval_supervisor", "error", "ERROR", {"error_type": type(exc).__name__})
            return self._terminal(result, FinalState.FAILED, "retrieval tool failure")
        result["retrieval_candidates"] = candidates
        return self._finish(
            result,
            "retrieval_supervisor",
            route="fuse",
            reason="specialist barrier complete",
            output=candidates,
        )

    def _fusion_rerank(self, state: GraphState) -> GraphState:
        result = self._enter(state, "fusion_rerank_agent", WorkflowState.CHECKING_EVIDENCE)
        if result.get("final_state"):
            return result
        case = result["normalized_case"] or {}
        profile = _configuration_profile(case)
        pinned_revisions = {
            (item["document_id"], item["revision_id"])
            for item in result["ingestion_snapshot"]["documents"]
        }
        merged: dict[str, dict[str, Any]] = {}
        for candidate in result.get("retrieval_candidates", []):
            evidence_id = candidate.get("evidence_id")
            if not evidence_id:
                continue
            if evidence_id not in merged:
                merged[evidence_id] = copy.deepcopy(candidate)
                merged[evidence_id].setdefault("retrieval_scores", {})
            else:
                merged[evidence_id].setdefault("retrieval_scores", {}).update(
                    candidate.get("retrieval_scores", {})
                )

        validated: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for candidate in merged.values():
            repositories_ok = candidate.get("source_repository") == "synthetic-demo-corpus"
            snapshot_ok = (
                candidate.get("document_id"),
                candidate.get("revision_id"),
            ) in pinned_revisions
            aircraft_ok = case.get("aircraft_type") in candidate.get("aircraft_types", [])
            config_ok = profile in candidate.get("configurations", [])
            historical = candidate.get("source_authority") == "HISTORICAL_CONTEXT"
            gate_ok = (
                repositories_ok
                and snapshot_ok
                and aircraft_ok
                and config_ok
                and candidate.get("approval_status") == "APPROVED"
                and candidate.get("revision_status") == "CURRENT"
                and candidate.get("applicability_status") == "PASS"
                and not historical
            )
            scores = candidate.get("retrieval_scores", {})
            candidate["fusion_score"] = round(
                0.35 * float(scores.get("semantic", 0))
                + 0.25 * float(scores.get("lexical", 0))
                + 0.25 * float(scores.get("exact", 0))
                + 0.15 * float(scores.get("graph", 0)),
                6,
            )
            if gate_ok:
                validated.append(candidate)
            elif not historical:
                candidate["rejection_reasons"] = [
                    name
                    for name, passed in {
                        "source_allow_list": repositories_ok,
                        "source_snapshot": snapshot_ok,
                        "aircraft_effectivity": aircraft_ok,
                        "configuration_effectivity": config_ok,
                        "approval": candidate.get("approval_status") == "APPROVED",
                        "revision": candidate.get("revision_status") == "CURRENT",
                        "applicability": candidate.get("applicability_status") == "PASS",
                    }.items()
                    if not passed
                ]
                rejected.append(candidate)
        validated.sort(
            key=lambda item: (item["fusion_score"], item.get("reference_number", "")), reverse=True
        )
        result["validated_evidence"] = validated[:10]
        result["rejected_evidence"] = rejected
        self._log(
            "fusion_rerank_agent",
            "gate",
            "PASS" if validated else "FAIL",
            {
                "eligible": len(validated),
                "rejected": len(rejected),
                "reranked": len(validated[:10]),
            },
        )
        if not validated:
            return self._terminal(result, FinalState.ABSTAINED, "no eligible evidence")
        return self._finish(
            result,
            "fusion_rerank_agent",
            route="gates",
            reason="prefilter, fusion, rerank complete",
        )

    def _gate_team(self, state: GraphState) -> GraphState:
        result = self._enter(state, "evidence_gate_supervisor", WorkflowState.CHECKING_EVIDENCE)
        if result.get("final_state"):
            return result
        case = result["normalized_case"] or {}
        entered = set(case.get("entered_references", []))
        evidence = copy.deepcopy(result.get("validated_evidence", []))
        relevant = [item for item in evidence if item.get("reference_number") in entered]
        if not relevant:
            relevant = evidence[:1]
        cross_refs: list[dict[str, Any]] = []
        unresolved = False
        try:
            for source in relevant:
                for raw_ref in source.get("cross_references", []):
                    ref = CrossReference(
                        from_evidence_id=source["evidence_id"],
                        reference_type=raw_ref.get("reference_type", "OTHER"),
                        target_reference=raw_ref["target_reference"],
                        mandatory=bool(raw_ref.get("mandatory")),
                        retrieval_attempts=1,
                    )
                    resolution, result = self._tool(
                        result,
                        "cross_reference_resolver",
                        "resolve_cross_reference",
                        lambda target=ref.target_reference, src=source: (
                            self.corpus.resolve_cross_reference(target, source_context=src)
                        ),
                    )
                    target_doc = (
                        resolution.get("evidence") if isinstance(resolution, dict) else None
                    )
                    if target_doc:
                        target_valid = (
                            target_doc.get("approval_status") == "APPROVED"
                            and target_doc.get("revision_status") == "CURRENT"
                            and target_doc.get("applicability_status") == "PASS"
                            and case.get("aircraft_type") in target_doc.get("aircraft_types", [])
                            and _configuration_profile(case) in target_doc.get("configurations", [])
                        )
                        if target_valid:
                            ref.status = "RESOLVED"
                            ref.resolved_evidence_id = target_doc["evidence_id"]
                            if all(x["evidence_id"] != target_doc["evidence_id"] for x in evidence):
                                target_doc = copy.deepcopy(target_doc)
                                target_doc.setdefault("retrieval_scores", {})["graph"] = 1.0
                                evidence.append(target_doc)
                        else:
                            ref.status = "UNRESOLVED"
                    else:
                        ref.status = "NOT_IN_CORPUS"
                    if ref.mandatory and ref.status != "RESOLVED":
                        unresolved = True
                    cross_refs.append(ref.model_dump(mode="json"))
        except BudgetExceeded as exc:
            return self._terminal(result, FinalState.ABSTAINED, str(exc))
        except Exception as exc:
            self._log(
                "cross_reference_resolver", "error", "ERROR", {"error_type": type(exc).__name__}
            )
            return self._terminal(result, FinalState.FAILED, "cross-reference tool failure")

        conflicts: list[dict[str, Any]] = []
        current_by_canonical: dict[str, list[dict[str, Any]]] = {}
        for item in evidence:
            canonical = item.get("canonical_reference")
            if canonical:
                current_by_canonical.setdefault(canonical, []).append(item)
        for canonical, items in current_by_canonical.items():
            revisions = {item.get("revision_id") for item in items}
            if len(revisions) > 1:
                conflicts.append(
                    {
                        "conflict_id": f"CON-{canonical}",
                        "conflict_type": "REVISION",
                        "evidence_ids": [item["evidence_id"] for item in items],
                        "description": (
                            "Multiple current revisions found for one canonical reference."
                        ),
                        "material": True,
                        "resolution_status": "UNRESOLVED",
                        "human_resolution": None,
                    }
                )
        result["validated_evidence"] = evidence
        result["cross_references"] = cross_refs
        result["conflicts"] = conflicts
        result["gate_results"] = {
            "applicability": "PASS",
            "revision": "PASS",
            "approval": "PASS",
            "cross_reference": "INCOMPLETE" if unresolved else "COMPLETE",
            "conflict": "FAIL" if conflicts else "PASS",
        }
        for gate, status in result["gate_results"].items():
            self._log("evidence_gate_supervisor", "gate", status, {"gate": gate})
        if conflicts:
            return self._terminal(result, FinalState.ESCALATED, "unresolved material conflict")
        if unresolved:
            loops = result["counters"]["retrieval_loops"]
            if loops < result["limits"]["max_retrieval_loops"]:
                targets = [x["target_reference"] for x in cross_refs if x["status"] != "RESOLVED"]
                result["search_tasks"] = [
                    SearchTask(
                        source_type="AMM",
                        objective="resolve mandatory cross-reference",
                        query=target,
                        filters={"aircraft_type": case.get("aircraft_type")},
                        target_reference=target,
                    ).model_dump(mode="json")
                    for target in targets
                ]
                self._log(
                    "orchestrator",
                    "retry",
                    "BOUNDED",
                    {"targets": targets, "next_loop": loops + 1},
                )
                return self._finish(
                    result,
                    "evidence_gate_supervisor",
                    route="plan",
                    reason="mandatory reference unresolved",
                )
            return self._terminal(
                result,
                FinalState.ABSTAINED,
                "mandatory reference unresolved; loop budget exhausted",
            )
        return self._finish(
            result,
            "evidence_gate_supervisor",
            route="synthesize",
            reason="deterministic evidence gates pass",
        )

    def _synthesize(self, state: GraphState) -> GraphState:
        result = self._enter(state, "synthesis_agent", WorkflowState.DRAFTING_PACKAGE)
        if result.get("final_state"):
            return result
        case = result["normalized_case"] or {}
        evidence = result.get("validated_evidence", [])
        evidence_by_id = {item["evidence_id"]: item for item in evidence}
        entered = set(case.get("entered_references", []))
        claims: list[dict[str, Any]] = []
        for item in evidence:
            if item.get("reference_number") not in entered:
                continue
            claim = Claim(
                claim_id=f"CLM-{len(claims) + 1:03d}",
                claim_text=(
                    f"Reference {item['reference_number']} is current, approved, and applicable to "
                    "the supplied synthetic aircraft context."
                ),
                claim_type="FACT",
                evidence_ids=[item["evidence_id"]],
                support_status="SUPPORTED",
                validator_results=[{"gate": "citation", "status": "PASS"}],
            )
            claims.append(claim.model_dump(mode="json"))
        for ref in result.get("cross_references", []):
            if ref.get("status") == "RESOLVED":
                ids = [ref["from_evidence_id"], ref["resolved_evidence_id"]]
                claims.append(
                    Claim(
                        claim_id=f"CLM-{len(claims) + 1:03d}",
                        claim_text=(
                            f"{ref['target_reference']} is the resolved mandatory linked reference."
                        ),
                        claim_type="RECOMMENDED_REFERENCE",
                        evidence_ids=ids,
                        support_status="SUPPORTED",
                        validator_results=[{"gate": "citation", "status": "PASS"}],
                    ).model_dump(mode="json")
                )
        citation_failures = [
            claim["claim_id"]
            for claim in claims
            if not claim["evidence_ids"]
            or any(evidence_id not in evidence_by_id for evidence_id in claim["evidence_ids"])
        ]
        self._log(
            "citation_validator",
            "gate",
            "FAIL" if citation_failures else "PASS",
            {"failed_claim_ids": citation_failures},
        )
        if citation_failures or not claims:
            return self._terminal(
                result, FinalState.ABSTAINED, "atomic claims lack resolvable evidence"
            )
        result["claims"] = claims
        for claim in claims:
            for evidence_id in claim["evidence_ids"]:
                links = evidence_by_id[evidence_id].setdefault("supports_claim_ids", [])
                if claim["claim_id"] not in links:
                    links.append(claim["claim_id"])
        package = ReviewPackage(
            case_id=result["case_id"],
            run_id=result["run_id"],
            final_state=FinalState.REVIEW_READY,
            case_summary=case.get("defect_description", ""),
            normalized_case=case,
            assumptions=["Synthetic demo corpus; operational use prohibited."],
            missing_information=[],
            plan_summary=[str(item.get("step", "")) for item in result.get("plan", [])],
            claims=claims,
            evidence=[_evidence_item(item) for item in evidence],
            recommended_references=[
                {"reference": item.get("reference_number"), "evidence_id": item["evidence_id"]}
                for item in evidence
            ],
            applicability_checks=[
                {"evidence_id": item["evidence_id"], "status": "PASS"} for item in evidence
            ],
            revision_checks=[
                {"evidence_id": item["evidence_id"], "status": "CURRENT"} for item in evidence
            ],
            approval_checks=[
                {"evidence_id": item["evidence_id"], "status": "APPROVED"} for item in evidence
            ],
            cross_references=result.get("cross_references", []),
            conflicts=result.get("conflicts", []),
            limitations=[
                "Synthetic evidence only; controlled operational sources must be opened "
                "by a human.",
                *result.get("execution_warnings", []),
            ],
            required_human_actions=[
                "Open every cited controlled source and make the governed decision."
            ],
            human_authority_notice=HUMAN_AUTHORITY_NOTICE,
            source_snapshot_id=result["source_snapshot_id"],
            workflow_version=result["workflow_version"],
            langfuse_trace_id=result["trace_context"]["langfuse_trace_id"],
        )
        result["review_package"] = package.model_dump(mode="json")
        result["gate_results"]["citation"] = "PASS"
        result["gate_results"]["completeness"] = "PASS"
        return self._finish(
            result,
            "synthesis_agent",
            route="critic",
            reason="cited review package drafted",
            output=result["review_package"],
        )

    def _critic(self, state: GraphState) -> GraphState:
        result = self._enter(state, "independent_critic", WorkflowState.CRITIC_REVIEW)
        if result.get("final_state"):
            return result
        package = result.get("review_package") or {}
        deterministic_findings: list[dict[str, Any]] = []
        if not package.get("human_authority_notice"):
            deterministic_findings.append({"code": "MISSING_AUTHORITY_NOTICE", "material": True})
        evidence_ids = {item.get("evidence_id") for item in package.get("evidence", [])}
        for claim in package.get("claims", []):
            if any(item not in evidence_ids for item in claim.get("evidence_ids", [])):
                deterministic_findings.append(
                    {
                        "code": "UNRESOLVED_CITATION",
                        "claim_id": claim.get("claim_id"),
                        "material": True,
                    }
                )
        if any(
            ref.get("mandatory") and ref.get("status") != "RESOLVED"
            for ref in package.get("cross_references", [])
        ):
            deterministic_findings.append(
                {"code": "UNRESOLVED_MANDATORY_REFERENCE", "material": True}
            )

        def fallback() -> dict[str, Any]:
            return {"valid": not deterministic_findings, "findings": []}

        try:
            response, result = self._model_call(
                result,
                actor="independent_critic",
                system=(
                    "Read-only critic. Return JSON {valid:boolean, findings:array}. "
                    "Check atomic claims, citation IDs, mandatory references, "
                    "human-authority notice, and final-state consistency. "
                    "Do not add maintenance advice or override deterministic gates."
                ),
                payload={
                    "case_id": result["case_id"],
                    "source_snapshot_id": result["source_snapshot_id"],
                    "claims": package.get("claims", []),
                    "evidence_ids": sorted(evidence_ids),
                    "cross_references": package.get("cross_references", []),
                    "gate_results": result.get("gate_results", {}),
                    "human_authority_notice_present": bool(package.get("human_authority_notice")),
                },
                fallback=fallback,
            )
        except BudgetExceeded as exc:
            return self._terminal(result, FinalState.ABSTAINED, str(exc))
        model_findings = response.value.get("findings", [])
        if not isinstance(model_findings, list):
            model_findings = [{"code": "INVALID_CRITIC_SCHEMA", "material": True}]
        findings = deterministic_findings + [
            item for item in model_findings if isinstance(item, dict)
        ]
        model_valid = response.value.get("valid") is True
        result["critic_findings"] = findings
        if deterministic_findings:
            return self._terminal(
                result, FinalState.ABSTAINED, "critic confirmed deterministic package failure"
            )
        if not model_valid or findings:
            counters = Counters.model_validate(result["counters"])
            if (
                counters.critic_retries < 1
                and counters.retrieval_loops < result["limits"]["max_retrieval_loops"]
            ):
                counters.critic_retries += 1
                result["counters"] = counters.model_dump()
                return self._finish(
                    result,
                    "independent_critic",
                    route="plan",
                    reason="critic requested one bounded recheck",
                )
            return self._terminal(result, FinalState.ABSTAINED, "critic findings unresolved")
        limitations = result["review_package"].setdefault("limitations", [])
        for warning in result.get("execution_warnings", []):
            if warning not in limitations:
                limitations.append(warning)
        result["final_state"] = FinalState.REVIEW_READY.value
        result["workflow_state"] = WorkflowState.REVIEW_READY.value
        result["review_package"]["final_state"] = FinalState.REVIEW_READY.value
        return self._finish(result, "independent_critic", route="finalize", reason="critic pass")

    def _finalize(self, state: GraphState) -> GraphState:
        result = copy.deepcopy(state)
        final = result.get("final_state") or FinalState.FAILED.value
        result["final_state"] = final
        if result.get("review_package") is None:
            case = result.get("normalized_case") or result.get("raw_input", {})
            result["review_package"] = ReviewPackage(
                case_id=result["case_id"],
                run_id=result["run_id"],
                final_state=FinalState(final),
                case_summary=str(case.get("defect_description", "")),
                normalized_case=case,
                missing_information=result.get("validation_issues", []),
                plan_summary=[str(item.get("step", "")) for item in result.get("plan", [])],
                claims=result.get("claims", []),
                evidence=[_evidence_item(item) for item in result.get("validated_evidence", [])],
                cross_references=result.get("cross_references", []),
                conflicts=result.get("conflicts", []),
                limitations=[
                    result.get("route_reason", "workflow stopped safely"),
                    "Synthetic demo data only.",
                    *result.get("execution_warnings", []),
                ],
                required_human_actions=[
                    "Supply missing governed data or evidence before rerunning."
                ]
                if final != FinalState.REVIEW_READY
                else [],
                human_authority_notice=HUMAN_AUTHORITY_NOTICE,
                source_snapshot_id=result["source_snapshot_id"],
                workflow_version=result["workflow_version"],
                langfuse_trace_id=result["trace_context"]["langfuse_trace_id"],
            ).model_dump(mode="json")
        result["trace_context"]["local_trace_path"] = str(self.logger.path) if self.logger else None
        self._log(
            "orchestrator",
            "terminal",
            "OK",
            {
                "final_state": final,
                "reason": result.get("route_reason"),
                "counters": result["counters"],
                "token_usage": result["token_usage"],
                "expected_final_state": result.get("expected_final_state"),
            },
        )
        return result

    @staticmethod
    def _next_or_finalize(state: GraphState, next_node: str) -> str:
        return "finalize" if state.get("final_state") else next_node

    def build_graph(self) -> Any:
        graph = StateGraph(GraphState)
        graph.add_node("normalize", self._normalize)
        graph.add_node("validate", self._validate)
        graph.add_node("plan", self._plan)
        graph.add_node("retrieve", self._retrieval_team)
        graph.add_node("fuse", self._fusion_rerank)
        graph.add_node("gates", self._gate_team)
        graph.add_node("synthesize", self._synthesize)
        graph.add_node("critic", self._critic)
        graph.add_node("finalize", self._finalize)
        graph.add_edge(START, "normalize")
        graph.add_conditional_edges(
            "normalize",
            lambda s: self._next_or_finalize(s, "validate"),
            {"validate": "validate", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "validate",
            lambda s: self._next_or_finalize(s, "plan"),
            {"plan": "plan", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "plan",
            lambda s: self._next_or_finalize(s, "retrieve"),
            {"retrieve": "retrieve", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "retrieve",
            lambda s: self._next_or_finalize(s, "fuse"),
            {"fuse": "fuse", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "fuse",
            lambda s: self._next_or_finalize(s, "gates"),
            {"gates": "gates", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "gates",
            lambda s: s.get("route", "finalize"),
            {"plan": "plan", "synthesize": "synthesize", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "synthesize",
            lambda s: self._next_or_finalize(s, "critic"),
            {"critic": "critic", "finalize": "finalize"},
        )
        graph.add_conditional_edges(
            "critic", lambda s: s.get("route", "finalize"), {"plan": "plan", "finalize": "finalize"}
        )
        graph.add_edge("finalize", END)
        return graph.compile()

    def run(
        self, raw_input: dict[str, Any], *, expected_final_state: str | None = None
    ) -> GraphState:
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        case_id = str(raw_input.get("case_id") or f"case-{uuid.uuid4().hex[:8]}")
        correlation_id = f"corr-{uuid.uuid4().hex[:12]}"
        trace_id = uuid.uuid4().hex
        self.logger = get_logger(
            log_dir=Path(self.settings.log_dir),
            run_id=run_id,
            case_id=case_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
        )
        self.model = JSONModelClient(self.settings, self.logger)
        self.telemetry = LangfuseTelemetry(self.settings, self.logger)
        self.deep_agent = DeepAgentHarness(
            settings=self.settings,
            corpus=self.corpus,
            logger=self.logger,
            telemetry=self.telemetry,
        )
        limits = ExecutionLimits(
            max_graph_steps=min(self.settings.max_graph_steps, self.settings.max_turns, 40),
            max_retrieval_loops=self.settings.max_retrieval_loops,
            max_tool_calls=self.settings.max_tool_calls,
            max_model_calls=self.settings.max_model_calls,
            max_total_tokens=self.settings.max_total_tokens,
            max_runtime_seconds=self.settings.max_runtime_seconds,
        )
        ingestion_snapshot = self.corpus.snapshot_manifest
        initial: GraphState = {
            "run_id": run_id,
            "case_id": case_id,
            "workflow_version": self.settings.workflow_version,
            "prompt_versions": {
                **self.settings.prompt_versions,
                "profile": self.settings.prompt_profile,
            },
            "source_snapshot_id": self.corpus.source_snapshot_id,
            "ingestion_snapshot": ingestion_snapshot.model_dump(mode="json"),
            "raw_input": copy.deepcopy(raw_input),
            "normalized_case": None,
            "validation_issues": [],
            "plan": [],
            "search_tasks": [],
            "retrieval_candidates": [],
            "validated_evidence": [],
            "rejected_evidence": [],
            "cross_references": [],
            "conflicts": [],
            "claims": [],
            "review_package": None,
            "critic_findings": [],
            "gate_results": {},
            "workflow_state": WorkflowState.DRAFT.value,
            "final_state": None,
            "human_review": None,
            "counters": Counters().model_dump(),
            "token_usage": TokenUsage().model_dump(),
            "limits": limits.model_dump(),
            "trace_context": TraceContext(
                langfuse_trace_id=trace_id, correlation_id=correlation_id
            ).model_dump(),
            "route": "normalize",
            "route_reason": "new run",
            "started_monotonic": time.monotonic(),
            "expected_final_state": expected_final_state,
            "execution_warnings": [],
        }
        self._log(
            "orchestrator",
            "run_start",
            "OK",
            {
                "workflow_version": self.settings.workflow_version,
                "model": self.settings.openai_model,
                "prompt_profile": self.settings.prompt_profile,
                "base_url": self.settings.openai_base_url,
                "source_snapshot_id": self.corpus.source_snapshot_id,
                "snapshot_digest": ingestion_snapshot.snapshot_digest,
                "ingested_document_count": len(ingestion_snapshot.documents),
                "synthetic": True,
                "deep_agent_enabled": self.settings.enable_deep_agent,
                "langfuse_enabled": self.telemetry.enabled if self.telemetry else False,
                "limits": limits.model_dump(),
            },
        )
        graph = self.build_graph()
        client = self.telemetry.client() if self.telemetry else None
        if client is not None:
            try:
                from langfuse import propagate_attributes

                with client.start_as_current_observation(
                    as_type="span",
                    name="defect_analysis",
                    trace_context={"trace_id": trace_id},
                ) as span:
                    with propagate_attributes(
                        session_id=case_id,
                        user_id=str(raw_input.get("created_by") or "demo-user"),
                        tags=["aabw", "aircraft-maintenance", "defect-analysis"],
                    ):
                        span.update(
                            input={
                                "case_id": case_id,
                                "synthetic": raw_input.get("synthetic", True),
                            },
                            metadata={
                                "workflow_version": self.settings.workflow_version,
                                "prompt_profile": self.settings.prompt_profile,
                                "source_snapshot_id": self.corpus.source_snapshot_id,
                            },
                        )
                        result = graph.invoke(
                            initial,
                            config={"recursion_limit": min(self.settings.max_turns, 40)},
                        )
                        span.update(
                            output={
                                "final_state": result.get("final_state"),
                                "run_id": result.get("run_id"),
                            }
                        )
            except Exception as exc:  # pragma: no cover - Langfuse failures are external
                self._log(
                    "langfuse",
                    "trace",
                    "ERROR",
                    {"error_type": type(exc).__name__, "fallback": "local_trace"},
                )
                result = graph.invoke(
                    initial,
                    config={"recursion_limit": min(self.settings.max_turns, 40)},
                )
        else:
            result = graph.invoke(
                initial,
                config={"recursion_limit": min(self.settings.max_turns, 40)},
            )
        if self.telemetry:
            self.telemetry.flush()
        return result
