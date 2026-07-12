"""Benchmark matrix runner for AABW demo evidence.

Runs multiple models and prompt profiles against a fixed synthetic dataset,
emits deterministic scores to Langfuse when enabled, optionally uses an LLM judge,
and writes local JSONL/summary artifacts for the pitch appendix.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests

from .config import Settings
from .evaluate import evaluate_fixture, load_jsonl
from .synthetic_data import DEFAULT_CASES_OUT, DEFAULT_CORPUS_OUT, generate

DEFAULT_MODELS = ["gpt-4o-mini"]
DEFAULT_PROMPT_PROFILES = ["safety_default", "strict_abstention", "retrieval_broad"]


def _split_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _settings_for(
    *,
    base: Settings,
    model: str,
    prompt_profile: str,
    corpus_path: Path,
    offline: bool,
    fixture: dict[str, Any],
) -> Settings:
    overrides = fixture.get("settings_overrides", {})
    data = {
        **base.model_dump(),
        "openai_model": model,
        "deep_agent_model": model,
        "prompt_profile": prompt_profile,
        "corpus_path": corpus_path,
        "offline": offline,
        "prompt_versions": {
            **base.prompt_versions,
            "profile": prompt_profile,
            "benchmark_model": model,
        },
        **overrides,
    }
    return Settings(**data)


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["model"], record["prompt_profile"])].append(record)
    rows = []
    for (model, prompt), items in sorted(groups.items()):
        latencies = [item["latency_ms"] for item in items]
        p95_index = max(0, int(len(latencies) * 0.95) - 1)
        rows.append(
            {
                "model": model,
                "prompt_profile": prompt,
                "examples": len(items),
                "passed": sum(item["passed"] for item in items),
                "failed": sum(not item["passed"] for item in items),
                "pass_rate": round(sum(item["passed"] for item in items) / len(items), 4),
                "avg_latency_ms": round(statistics.mean(latencies), 2),
                "p95_latency_ms": round(sorted(latencies)[p95_index], 2),
                "review_ready_precision": _review_ready_precision(items),
                "safe_non_review_ready_recall": _safe_non_review_ready_recall(items),
                "score_means": _score_means(items),
                "category_means": _category_means(items),
                "synthetic": True,
            }
        )
    return {
        "matrix": rows,
        "total_runs": len(records),
        "total_passed": sum(record["passed"] for record in records),
        "total_failed": sum(not record["passed"] for record in records),
        "synthetic": True,
    }


def _review_ready_precision(items: list[dict[str, Any]]) -> float | None:
    predicted = [item for item in items if item["actual_final_state"] == "REVIEW_READY"]
    if not predicted:
        return None
    correct = [
        item for item in predicted if item["expected_final_state"] == item["actual_final_state"]
    ]
    return round(len(correct) / len(predicted), 4)


def _safe_non_review_ready_recall(items: list[dict[str, Any]]) -> float:
    negative = [item for item in items if item["expected_final_state"] != "REVIEW_READY"]
    if not negative:
        return 1.0
    safe_states = {"NEEDS_CLARIFICATION", "ESCALATED", "ABSTAINED", "FAILED"}
    routed_safe = [item for item in negative if item["actual_final_state"] in safe_states]
    return round(len(routed_safe) / len(negative), 4)


def _score_means(items: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for item in items:
        for score in item.get("scores", []):
            if isinstance(score.get("value"), int | float):
                values[str(score["name"])].append(float(score["value"]))
    return {
        name: round(statistics.mean(score_values), 4)
        for name, score_values in sorted(values.items())
        if score_values
    }


def _category_means(items: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for item in items:
        for score in item.get("scores", []):
            metadata = score.get("metadata", {})
            category = str(metadata.get("category", "uncategorized"))
            if isinstance(score.get("value"), int | float):
                values[category].append(float(score["value"]))
    return {
        category: round(statistics.mean(score_values), 4)
        for category, score_values in sorted(values.items())
        if score_values
    }


def _write_outputs(output_dir: Path, records: list[dict[str, Any]]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "benchmark_results.jsonl"
    summary_path = output_dir / "benchmark_summary.json"
    scores_path = output_dir / "benchmark_scores.csv"
    results_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    with scores_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "model",
                "prompt_profile",
                "case_id",
                "score_name",
                "score_value",
                "category",
                "expected_final_state",
                "actual_final_state",
            ],
        )
        writer.writeheader()
        for record in records:
            for score in record.get("scores", []):
                metadata = score.get("metadata", {})
                writer.writerow(
                    {
                        "model": record.get("model"),
                        "prompt_profile": record.get("prompt_profile"),
                        "case_id": record.get("case_id"),
                        "score_name": score.get("name"),
                        "score_value": score.get("value"),
                        "category": metadata.get("category"),
                        "expected_final_state": record.get("expected_final_state"),
                        "actual_final_state": record.get("actual_final_state"),
                    }
                )
    summary = _aggregate(records)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"results": results_path, "summary": summary_path, "scores": scores_path}


def _fetch_langfuse_scores(settings: Settings, trace_ids: list[str]) -> dict[str, Any]:
    if not (
        settings.enable_langfuse
        and settings.langfuse_public_key
        and settings.langfuse_secret_key
        and trace_ids
    ):
        return {"enabled": False, "reason": "langfuse_disabled_or_no_trace_ids"}
    base_url = settings.langfuse_base_url.rstrip("/")
    auth = (settings.langfuse_public_key, settings.langfuse_secret_key)
    summaries: list[dict[str, Any]] = []
    for trace_id in trace_ids[:25]:
        try:
            response = requests.get(
                f"{base_url}/api/public/v3/scores",
                params={"traceId": trace_id, "limit": 100},
                auth=auth,
                timeout=10,
            )
            if response.status_code == 404:
                response = requests.get(
                    f"{base_url}/api/public/scores",
                    params={"traceId": trace_id, "limit": 100},
                    auth=auth,
                    timeout=10,
                )
            if response.status_code >= 400:
                summaries.append(
                    {
                        "trace_id": trace_id,
                        "status": response.status_code,
                        "scores": [],
                    }
                )
                continue
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else payload
            scores = data if isinstance(data, list) else []
            summaries.append(
                {
                    "trace_id": trace_id,
                    "status": response.status_code,
                    "score_count": len(scores),
                    "scores": [
                        {
                            "name": item.get("name"),
                            "value": item.get("value"),
                            "dataType": item.get("dataType") or item.get("data_type"),
                        }
                        for item in scores[:20]
                        if isinstance(item, dict)
                    ],
                }
            )
        except Exception as exc:
            summaries.append(
                {"trace_id": trace_id, "status": "ERROR", "error_type": type(exc).__name__}
            )
    return {"enabled": True, "traces_checked": len(summaries), "traces": summaries}


def run_benchmark(
    *,
    corpus_path: Path,
    cases_path: Path,
    output_dir: Path,
    models: list[str],
    prompt_profiles: list[str],
    offline: bool,
    limit: int | None = None,
) -> dict[str, Any]:
    base = Settings()
    fixtures = load_jsonl(cases_path)
    if limit is not None:
        fixtures = fixtures[:limit]
    records: list[dict[str, Any]] = []
    started = time.perf_counter()
    for model in models:
        for prompt_profile in prompt_profiles:
            for fixture in fixtures:
                settings = _settings_for(
                    base=base,
                    model=model,
                    prompt_profile=prompt_profile,
                    corpus_path=corpus_path,
                    offline=offline,
                    fixture=fixture,
                )
                record = evaluate_fixture(fixture, settings)
                record["model"] = model
                record["prompt_profile"] = prompt_profile
                record["settings_overrides"] = fixture.get("settings_overrides", {})
                records.append(record)
                failed_checks = [
                    name for name, passed in record.get("checks", {}).items() if not passed
                ]
                print(
                    json.dumps(
                        {
                            "case_id": record["case_id"],
                            "model": model,
                            "prompt_profile": prompt_profile,
                            "expected_final_state": record["expected_final_state"],
                            "actual_final_state": record["actual_final_state"],
                            "passed": record["passed"],
                            "failed_checks": failed_checks,
                            "latency_ms": record["latency_ms"],
                            "langfuse_trace_id": record.get("langfuse_trace_id"),
                        },
                        ensure_ascii=False,
                    )
                )
    paths = _write_outputs(output_dir, records)
    trace_ids = [
        record["langfuse_trace_id"]
        for record in records
        if record.get("langfuse_trace_id")
    ]
    langfuse_fetch = _fetch_langfuse_scores(base, trace_ids)
    langfuse_path = output_dir / "langfuse_scores_snapshot.json"
    langfuse_path.write_text(json.dumps(langfuse_fetch, ensure_ascii=False, indent=2))
    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    summary["duration_seconds"] = round(time.perf_counter() - started, 2)
    summary["artifacts"] = {
        "results": str(paths["results"]),
        "summary": str(paths["summary"]),
        "scores": str(paths["scores"]),
        "langfuse_scores_snapshot": str(langfuse_path),
    }
    summary["langfuse_fetch"] = langfuse_fetch
    paths["summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AABW model/prompt benchmark matrix")
    parser.add_argument("--generate-data", action="store_true")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_OUT)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_OUT)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/benchmark"))
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--prompt-profiles", default=",".join(DEFAULT_PROMPT_PROFILES))
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--limit", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.generate_data or not args.corpus.exists() or not args.cases.exists():
        generated = generate(args.corpus, args.cases)
        print(json.dumps({"generated": generated}, ensure_ascii=False))
    summary = run_benchmark(
        corpus_path=args.corpus,
        cases_path=args.cases,
        output_dir=args.output_dir,
        models=_split_csv(args.models, DEFAULT_MODELS),
        prompt_profiles=_split_csv(args.prompt_profiles, DEFAULT_PROMPT_PROFILES),
        offline=args.offline,
        limit=args.limit,
    )
    print(json.dumps({"summary": summary}, ensure_ascii=False))
    return int(summary["total_failed"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
