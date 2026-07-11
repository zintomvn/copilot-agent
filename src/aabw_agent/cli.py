"""Command-line entry point for single runs and two-case demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import Settings
from .workflow import WorkflowRunner


def _read_cases(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else [payload]


def _summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": result["case_id"],
        "run_id": result["run_id"],
        "final_state": result["final_state"],
        "route_reason": result.get("route_reason"),
        "counters": result["counters"],
        "token_usage": result["token_usage"],
        "evidence": [item["evidence_id"] for item in result.get("validated_evidence", [])],
        "rejected_evidence": [item["evidence_id"] for item in result.get("rejected_evidence", [])],
        "trace": result["trace_context"].get("local_trace_path"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded aircraft evidence workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run curated synthetic cases")
    demo.add_argument("--examples", type=int, default=2)
    demo.add_argument("--dataset", type=Path, default=Path("data/eval_cases.jsonl"))
    demo.add_argument("--offline", action="store_true", help="use deterministic model fallbacks")
    run = subparsers.add_parser("run", help="run one JSON case")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--offline", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings(offline=args.offline)
    if args.command == "demo":
        fixtures = _read_cases(args.dataset)[: max(0, args.examples)]
        exit_code = 0
        for fixture in fixtures:
            raw = fixture.get("input_case", fixture)
            expected = fixture.get("expected_final_state")
            result = WorkflowRunner(settings=settings).run(raw, expected_final_state=expected)
            summary = _summary(result)
            summary["expected_final_state"] = expected
            summary["passed"] = expected is None or expected == result["final_state"]
            exit_code |= int(not summary["passed"])
            print(json.dumps(summary, ensure_ascii=False))
        return exit_code

    fixture = _read_cases(args.input)[0]
    raw = fixture.get("input_case", fixture)
    result = WorkflowRunner(settings=settings).run(
        raw, expected_final_state=fixture.get("expected_final_state")
    )
    print(json.dumps(_summary(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
