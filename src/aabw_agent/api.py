"""FastAPI demo API for the Aircraft Maintenance Decision Copilot."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Settings, get_settings
from .conversation import (
    ConversationCoordinator,
    ConversationSession,
    build_user_answer,
    cited_evidence,
    prompt_bundle,
)
from .evaluate import load_jsonl
from .pdf_ingest import build_corpus_from_pdf
from .workflow import WorkflowRunner


class RunCaseRequest(BaseModel):
    case: dict[str, Any]
    expected_final_state: str | None = None
    offline: bool | None = None
    include_events: bool = True


class ChatRequest(BaseModel):
    message: str
    case_id: str | None = None
    offline: bool | None = None
    include_events: bool = True
    custom_case: bool = False
    session_id: str | None = None
    choice_value: str | None = None


class ReviewActionRequest(BaseModel):
    run_id: str
    case_id: str
    reviewer_id: str
    action: str = Field(
        pattern="^(ACCEPT_FOR_FURTHER_REVIEW|REQUEST_CORRECTION|REJECT|ESCALATE|RESOLVE_CONFLICT)$"
    )
    comment: str | None = None
    resolved_conflict_ids: list[str] = Field(default_factory=list)


def _settings_with_overrides(offline: bool | None = None) -> Settings:
    settings = get_settings()
    corpus_path = settings.corpus_path
    benchmark_corpus = Path("data/benchmark_corpus.json")
    if corpus_path == Path("data/synthetic_corpus.json") and benchmark_corpus.exists():
        corpus_path = benchmark_corpus
    if offline is None:
        return Settings(**{**settings.model_dump(), "corpus_path": corpus_path})
    return Settings(**{**settings.model_dump(), "offline": offline, "corpus_path": corpus_path})


def _trace_events(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    trace_path = Path(path)
    if not trace_path.exists():
        return []
    return [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _demo_case_index() -> dict[str, dict[str, Any]]:
    cases_path = (
        Path("data/benchmark_cases.jsonl")
        if Path("data/benchmark_cases.jsonl").exists()
        else Path("data/eval_cases.jsonl")
    )
    return {item["case_id"]: item for item in load_jsonl(cases_path)}


def _case_from_chat(request: ChatRequest) -> tuple[dict[str, Any], str | None]:
    cases = _demo_case_index()
    message = request.message.strip()
    requested_case = request.case_id
    if not requested_case:
        for case_id in cases:
            if case_id.lower() in message.lower():
                requested_case = case_id
                break
    if requested_case and requested_case in cases:
        fixture = cases[requested_case]
        return fixture["input_case"], fixture.get("expected_final_state")

    references = sorted(set(re.findall(r"\bSYN-[A-Z0-9-]+\b", message.upper())))
    aircraft_match = re.search(r"\b(A320|A321|B737|B787|A350)\b", message.upper())
    config_match = re.search(r"\bSYN-CFG-[A-Z0-9-]+\b", message.upper())
    ata_match = re.search(r"\bATA\s*([0-9]{2})\b", message.upper())
    return (
        {
            "case_id": "CHAT-DEMO-001",
            "aircraft_registration": "SYN-CHAT",
            "aircraft_type": aircraft_match.group(1) if aircraft_match else "A320",
            "fleet_or_variant": "SYN-A320-DEMO",
            "configuration": {
                "profile": config_match.group(0) if config_match else "SYN-CFG-LG-A"
            },
            "ata_chapter": ata_match.group(1) if ata_match else "32",
            "defect_description": message,
            "reported_symptoms": [message],
            "flight_phase_or_context": "chat intake",
            "entered_references": references or ["SYN-MEL-CURRENT", "SYN-AMM-LINKED-CHECK"],
            "created_by": "chat-demo-user",
            "synthetic": True,
        },
        None,
    )


def _langfuse_trace_url(settings: Settings, trace_id: str | None) -> str | None:
    if not trace_id or not settings.enable_langfuse:
        return None
    return f"{settings.langfuse_base_url.rstrip('/')}/project/traces/{trace_id}"


_CUSTOM_CHAT_SESSIONS: dict[str, ConversationSession] = {}


def _workflow_response(
    result: dict[str, Any], settings: Settings, include_events: bool
) -> dict[str, Any]:
    events = _trace_events(result["trace_context"].get("local_trace_path"))
    trace_id = result["trace_context"].get("langfuse_trace_id")
    package = result.get("review_package") or {}
    return {
        "case_id": result["case_id"],
        "run_id": result["run_id"],
        "final_state": result["final_state"],
        "route_reason": result.get("route_reason"),
        "messages": _chat_transcript(result),
        "answer": build_user_answer(result),
        "trace_context": result["trace_context"],
        "langfuse_trace_url": _langfuse_trace_url(settings, trace_id),
        "tool_calls": [event for event in events if event.get("event_type") == "tool"],
        "events": events if include_events else [],
        "review_package": package,
        "citations": cited_evidence(package),
        "claims": package.get("claims", []),
        "gate_results": result.get("gate_results", {}),
        "cross_references": result.get("cross_references", []),
        "conflicts": result.get("conflicts", []),
        "system_prompts": prompt_bundle(settings.prompt_profile),
        "synthetic": True,
    }


def _choice_message(clarification: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "kind": "clarification",
        "content": clarification.get("question", ""),
        "items": clarification.get("options", []),
    }


def _custom_chat_response(
    request: ChatRequest,
    runner: WorkflowRunner,
    settings: Settings,
    coordinator: ConversationCoordinator,
) -> dict[str, Any]:
    session = _CUSTOM_CHAT_SESSIONS.get(request.session_id or "")
    if session is None:
        session = coordinator.start_session(request.message)
        _CUSTOM_CHAT_SESSIONS[session.session_id] = session
        turn = coordinator.continue_session(session)
    else:
        turn = coordinator.continue_session(
            session,
            message=None if request.choice_value else request.message,
            choice_value=request.choice_value,
        )
    if turn["status"] == "needs_clarification":
        clarification = turn["clarification"]
        return {
            "session_id": session.session_id,
            "case_id": turn["case_id"],
            "needs_clarification": True,
            "clarification": clarification,
            "messages": [_choice_message(clarification)],
            "draft_case": turn["draft_case"],
            "system_prompts": prompt_bundle(settings.prompt_profile),
            "synthetic": True,
        }

    result = runner.run(turn["case"])
    response = _workflow_response(result, settings, request.include_events)
    response["session_id"] = session.session_id
    response["needs_clarification"] = False
    response["draft_case"] = turn["case"]
    return response


def _chat_transcript(result: dict[str, Any]) -> list[dict[str, Any]]:
    package = result.get("review_package") or {}
    claims = package.get("claims", [])
    evidence = result.get("validated_evidence", [])
    rejected = result.get("rejected_evidence", [])
    conflicts = result.get("conflicts", [])
    gates = result.get("gate_results", {})
    tool_events = [
        event
        for event in _trace_events(result["trace_context"].get("local_trace_path"))
        if event.get("event_type") == "tool"
    ]
    return [
        {
            "role": "assistant",
            "kind": "status",
            "content": (
                f"Final state: {result['final_state']}. "
                f"Reason: {result.get('route_reason') or 'workflow completed'}."
            ),
        },
        {
            "role": "assistant",
            "kind": "plan",
            "content": "Plan: "
            + " -> ".join(str(item.get("step", "")) for item in result.get("plan", [])),
        },
        {
            "role": "assistant",
            "kind": "tools",
            "content": f"Tool calls executed: {len(tool_events)}.",
            "items": [
                {
                    "actor": event.get("actor"),
                    "tool": event.get("details", {}).get("tool"),
                    "status": event.get("status"),
                    "result_count": event.get("details", {}).get("result_count"),
                }
                for event in tool_events
            ],
        },
        {
            "role": "assistant",
            "kind": "gates",
            "content": "Evidence gates: "
            + ", ".join(f"{key}={value}" for key, value in gates.items()),
        },
        {
            "role": "assistant",
            "kind": "evidence",
            "content": (
                f"Accepted evidence: {len(evidence)}. "
                f"Rejected candidates: {len(rejected)}. Conflicts: {len(conflicts)}."
            ),
            "items": [
                {
                    "reference": item.get("reference_number"),
                    "evidence_id": item.get("evidence_id"),
                    "document_type": item.get("document_type"),
                    "location": item.get("page_or_location"),
                }
                for item in evidence
            ],
        },
        {
            "role": "assistant",
            "kind": "claims",
            "content": f"Cited claims: {len(claims)}.",
            "items": claims,
        },
        {
            "role": "assistant",
            "kind": "notice",
            "content": package.get("human_authority_notice", ""),
        },
    ]


def create_app() -> FastAPI:
    settings = get_settings()
    coordinator = ConversationCoordinator(WorkflowRunner(settings=settings).corpus)
    app = FastAPI(
        title="AABW Aircraft Maintenance Decision Copilot",
        version="0.1.0",
        description="Evidence-gated synthetic demo API. Not for operational maintenance use.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "workflow_version": settings.workflow_version,
            "synthetic": True,
            "deep_agent_enabled": settings.enable_deep_agent,
            "langfuse_enabled": settings.enable_langfuse,
        }

    @app.get("/demo/cases")
    def demo_cases() -> dict[str, Any]:
        cases_path = (
            Path("data/benchmark_cases.jsonl")
            if Path("data/benchmark_cases.jsonl").exists()
            else Path("data/eval_cases.jsonl")
        )
        cases = load_jsonl(cases_path)
        return {
            "source": str(cases_path),
            "cases": [
                {
                    "case_id": item["case_id"],
                    "expected_final_state": item.get("expected_final_state"),
                    "input_case": item["input_case"],
                }
                for item in cases
            ],
            "synthetic": True,
        }

    @app.post("/cases/run")
    def run_case(request: RunCaseRequest) -> dict[str, Any]:
        run_settings = _settings_with_overrides(request.offline)
        result = WorkflowRunner(settings=run_settings).run(
            request.case,
            expected_final_state=request.expected_final_state,
        )
        response = {
            "case_id": result["case_id"],
            "run_id": result["run_id"],
            "final_state": result["final_state"],
            "route_reason": result.get("route_reason"),
            "workflow_state": result.get("workflow_state"),
            "review_package": result.get("review_package"),
            "normalized_case": result.get("normalized_case"),
            "plan": result.get("plan", []),
            "gate_results": result.get("gate_results", {}),
            "validated_evidence": result.get("validated_evidence", []),
            "rejected_evidence": result.get("rejected_evidence", []),
            "cross_references": result.get("cross_references", []),
            "conflicts": result.get("conflicts", []),
            "critic_findings": result.get("critic_findings", []),
            "counters": result.get("counters", {}),
            "token_usage": result.get("token_usage", {}),
            "trace_context": result.get("trace_context", {}),
            "synthetic": True,
        }
        if request.include_events:
            response["events"] = _trace_events(result["trace_context"].get("local_trace_path"))
        return response

    @app.post("/chat")
    def chat(request: ChatRequest) -> dict[str, Any]:
        run_settings = _settings_with_overrides(request.offline)
        runner = WorkflowRunner(settings=run_settings)
        if request.custom_case:
            return _custom_chat_response(request, runner, run_settings, coordinator)
        case, expected = _case_from_chat(request)
        result = runner.run(
            case,
            expected_final_state=expected,
        )
        return _workflow_response(result, run_settings, request.include_events)

    @app.post("/runs/review")
    def record_review_action(request: ReviewActionRequest) -> dict[str, Any]:
        return {
            "review_id": f"review-{request.run_id}",
            "case_id": request.case_id,
            "run_id": request.run_id,
            "reviewer_id": request.reviewer_id,
            "action": request.action,
            "comment": request.comment,
            "resolved_conflict_ids": request.resolved_conflict_ids,
            "recorded": True,
            "notice": "Demo review action recorded in API response only; no production write-back.",
        }

    @app.post("/admin/ingest/pdf")
    async def ingest_pdf(
        pdf: Annotated[UploadFile, File(...)],
        manifest_json: Annotated[str, Form(...)],
    ) -> dict[str, Any]:
        try:
            manifest = json.loads(manifest_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="manifest_json must be valid JSON") from exc
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = settings.upload_dir / (pdf.filename or "upload.pdf")
        manifest_path = settings.upload_dir / f"{pdf_path.stem}.manifest.json"
        pdf_path.write_bytes(await pdf.read())
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        corpus = build_corpus_from_pdf(pdf_path, manifest_path)
        settings.ingested_corpus_path.parent.mkdir(parents=True, exist_ok=True)
        settings.ingested_corpus_path.write_text(
            json.dumps(corpus, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return {
            "output": str(settings.ingested_corpus_path),
            "documents": len(corpus["documents"]),
            "source_snapshot_id": corpus["source_snapshot_id"],
            "synthetic": True,
            "next_step": "Set CORPUS_PATH to this output and rerun the workflow.",
        }

    return app


app = create_app()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AABW demo API")
    parser.add_argument("--host", default=get_settings().api_host)
    parser.add_argument("--port", type=int, default=get_settings().api_port)
    parser.add_argument("--reload", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    uvicorn.run("aabw_agent.api:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
