"""Streaming evaluation runner for versioned JSONL cases."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from .config import Settings
from .workflow import WorkflowRunner


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def evaluate_fixture(fixture: dict[str, Any], settings: Settings) -> dict[str, Any]:
    started = time.perf_counter()
    result = WorkflowRunner(settings=settings).run(
        fixture["input_case"], expected_final_state=fixture.get("expected_final_state")
    )
    validated = result.get("validated_evidence", [])
    rejected = result.get("rejected_evidence", [])
    validated_ids = {item["evidence_id"] for item in validated}
    rejected_ids = {item["evidence_id"] for item in rejected}
    claim_ids = {
        evidence_id
        for claim in result.get("claims", [])
        for evidence_id in claim.get("evidence_ids", [])
    }
    actual_refs = {item.get("reference_number") for item in validated}
    checks = {
        "final_state": result["final_state"] == fixture.get("expected_final_state"),
        "expected_references": set(fixture.get("expected_references", [])) <= actual_refs,
        "expected_rejected": set(fixture.get("expected_rejected_evidence", [])) <= rejected_ids,
        "no_rejected_evidence_leakage": not bool(claim_ids & rejected_ids),
        "citations_resolve": claim_ids <= validated_ids,
        "graph_step_cap": result["counters"]["graph_steps"] <= min(settings.max_graph_steps, 40),
        "retrieval_loop_cap": result["counters"]["retrieval_loops"] <= settings.max_retrieval_loops,
        "tool_call_cap": result["counters"]["tool_calls"] <= settings.max_tool_calls,
        "token_cap": result["token_usage"]["total_tokens"] <= settings.max_total_tokens,
        "trace_complete": bool(result["trace_context"].get("local_trace_path")),
    }
    # Clarification cases intentionally retrieve nothing, so no reference expectations apply.
    if result["final_state"] == "NEEDS_CLARIFICATION":
        checks["expected_references"] = not fixture.get("expected_references")
        checks["expected_rejected"] = not fixture.get("expected_rejected_evidence")
    return {
        "case_id": fixture["case_id"],
        "expected_final_state": fixture.get("expected_final_state"),
        "actual_final_state": result["final_state"],
        "passed": all(checks.values()),
        "checks": checks,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "counters": result["counters"],
        "token_usage": result["token_usage"],
        "trace": result["trace_context"].get("local_trace_path"),
        "synthetic": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate bounded LangGraph cases")
    parser.add_argument("--input", type=Path, default=Path("data/eval_cases.jsonl"))
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings(offline=args.offline)
    records = [evaluate_fixture(fixture, settings) for fixture in load_jsonl(args.input)]
    for record in records:
        print(json.dumps(record, ensure_ascii=False))
    summary = {
        "examples": len(records),
        "passed": sum(record["passed"] for record in records),
        "failed": sum(not record["passed"] for record in records),
        "synthetic": True,
    }
    print(json.dumps({"summary": summary}, ensure_ascii=False))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
            encoding="utf-8",
        )
    return int(summary["failed"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
