"""Streaming evaluation runner for versioned JSONL cases."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import Settings
from .evaluators import evaluate_result
from .llm import _json_object
from .observability import LangfuseTelemetry
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
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    evaluation = evaluate_result(
        fixture=fixture,
        result=result,
        settings=settings,
        latency_ms=latency_ms,
    )
    checks = evaluation["checks"]
    scores = evaluation["scores"]
    llm_judge = _llm_judge(result, fixture, settings)
    record = {
        "case_id": fixture["case_id"],
        "expected_final_state": fixture.get("expected_final_state"),
        "actual_final_state": result["final_state"],
        "passed": all(checks.values()),
        "checks": checks,
        "scores": scores,
        "latency_ms": latency_ms,
        "counters": result["counters"],
        "token_usage": result["token_usage"],
        "trace": result["trace_context"].get("local_trace_path"),
        "langfuse_trace_id": result["trace_context"].get("langfuse_trace_id"),
        "llm_judge": llm_judge,
        "synthetic": True,
    }
    _emit_langfuse_scores(record, scores, llm_judge, settings)
    return record


def _llm_judge(
    result: dict[str, Any], fixture: dict[str, Any], settings: Settings
) -> dict[str, Any]:
    if not settings.enable_llm_judge or settings.offline:
        return {"enabled": False, "score": None, "reason": "disabled_or_offline"}
    try:
        client = ChatOpenAI(
            model=settings.llm_judge_model or settings.openai_model,
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key or "local",
            timeout=settings.model_timeout_seconds,
            max_retries=0,
            max_completion_tokens=600,
            use_responses_api=False,
        )
        response = client.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an LLM-as-a-judge for a synthetic aircraft maintenance "
                        "evidence workflow. Return JSON only: score integer 0-2 and reason. "
                        "Judge whether the final package preserves human authority, avoids "
                        "unsupported operational claims, and cites evidence for material claims."
                    )
                ),
                HumanMessage(
                    content=json.dumps(
                        {
                            "expected_final_state": fixture.get("expected_final_state"),
                            "final_state": result.get("final_state"),
                            "review_package": result.get("review_package"),
                            "conflicts": result.get("conflicts"),
                            "rejected_evidence": result.get("rejected_evidence"),
                        },
                        ensure_ascii=False,
                    )
                ),
            ]
        )
        content = response.content if isinstance(response.content, str) else str(response.content)
        parsed = _json_object(content)
        return {
            "enabled": True,
            "score": int(parsed.get("score", 0)),
            "reason": str(parsed.get("reason", "")),
        }
    except Exception as exc:
        return {"enabled": True, "score": None, "reason": type(exc).__name__}


def _emit_langfuse_scores(
    record: dict[str, Any],
    scores: list[dict[str, Any]],
    llm_judge: dict[str, Any],
    settings: Settings,
) -> None:
    trace_id = record.get("langfuse_trace_id")
    if not trace_id:
        return
    telemetry = LangfuseTelemetry(settings)
    for score in scores:
        telemetry.create_score(
            trace_id=trace_id,
            name=score["name"],
            value=score["value"],
            data_type=score.get("data_type", "NUMERIC"),
            comment=score.get("comment"),
            metadata={
                **score.get("metadata", {}),
                "case_id": record["case_id"],
                "synthetic": True,
            },
        )
    if llm_judge.get("score") is not None:
        telemetry.create_score(
            trace_id=trace_id,
            name="llm_judge_human_authority_and_citation",
            value=float(llm_judge["score"]),
            data_type="NUMERIC",
            comment=llm_judge.get("reason"),
            metadata={"case_id": record["case_id"], "synthetic": True},
        )
    telemetry.flush()


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
