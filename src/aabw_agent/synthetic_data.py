"""Generate curated synthetic data for AABW demo, benchmark, and pitch evidence.

The generated dataset is representative only. It deliberately covers the
submission and pitching playbook needs: visible agentic workflow, safe negative
cases, benchmark evidence, and synthetic-data disclosure.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .corpus import SyntheticCorpus

DEFAULT_CORPUS_OUT = Path("data/benchmark_corpus.json")
DEFAULT_CASES_OUT = Path("data/benchmark_cases.jsonl")


def _base_payload() -> dict[str, Any]:
    path = Path("data/synthetic_corpus.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _doc(
    *,
    document_id: str,
    evidence_id: str,
    document_type: str,
    title: str,
    reference_number: str,
    canonical_reference: str,
    revision_id: str,
    revision_date: str,
    approval_status: str = "APPROVED",
    revision_status: str = "CURRENT",
    source_authority: str = "AUTHORITATIVE",
    aircraft_types: list[str] | None = None,
    configurations: list[str] | None = None,
    applicability_status: str = "PASS",
    ata_chapter: str = "32",
    section_id: str = "SYN-SECTION",
    quoted_span: str = "Synthetic evidence span.",
    content: str = "Synthetic evidence content.",
    keywords: list[str] | None = None,
    cross_references: list[dict[str, Any]] | None = None,
    supersedes_revision: str | None = None,
) -> dict[str, Any]:
    aircraft = aircraft_types or ["A320"]
    configs = configurations or ["SYN-CFG-LG-A"]
    return {
        "document_id": document_id,
        "evidence_id": evidence_id,
        "document_type": document_type,
        "title": title,
        "reference_number": reference_number,
        "canonical_reference": canonical_reference,
        "revision_id": revision_id,
        "revision_date": revision_date,
        "supersedes_revision": supersedes_revision,
        "revision_status": revision_status,
        "approval_status": approval_status,
        "source_authority": source_authority,
        "aircraft_types": aircraft,
        "configurations": configs,
        "effectivity": {"aircraft_types": aircraft, "configurations": configs},
        "applicability_status": applicability_status,
        "ata_chapter": ata_chapter,
        "section_id": section_id,
        "page_or_location": f"{title}, {section_id}",
        "quoted_span": quoted_span,
        "content": content,
        "keywords": keywords or [],
        "cross_references": cross_references or [],
        "source_repository": "synthetic-demo-corpus",
        "source_uri": f"synthetic://aabw-benchmark/{document_id}/{revision_id}/{section_id}",
        "source_hash": f"sha256:{document_id.lower()}-{revision_id.lower()}",
        "synthetic": True,
    }


def build_benchmark_corpus() -> dict[str, Any]:
    payload = _base_payload()
    payload = deepcopy(payload)
    payload["corpus_id"] = "aabw-a320-benchmark-v1"
    payload["source_snapshot_id"] = "synthetic-snapshot-aabw-benchmark-2026-07-12-v1"
    payload["notice"] = (
        "SYNTHETIC BENCHMARK DATA. NOT AN APPROVED MAINTENANCE SOURCE. "
        "NOT FOR OPERATIONAL, AIRWORTHINESS, DISPATCH, OR RELEASE-TO-SERVICE DECISIONS."
    )
    additions = [
        _doc(
            document_id="SYN-TSM-DOOR-FAULT",
            evidence_id="EV-SYN-TSM-DOOR-FAULT-52-10",
            document_type="TSM",
            title="Synthetic A320 TSM - Door Proximity Fault",
            reference_number="SYN-TSM-DOOR-FAULT",
            canonical_reference="SYN-TSM-52-10-FAULT",
            revision_id="R2",
            revision_date="2026-05-20",
            ata_chapter="52",
            section_id="TSM-52-10-00-FI",
            quoted_span=(
                "For an intermittent passenger door proximity message on A320 configuration "
                "SYN-CFG-LG-A, use the synthetic fault isolation task and record results for "
                "authorized review."
            ),
            content=(
                "Intermittent passenger door proximity message. Synthetic TSM fault isolation "
                "applies to A320 configuration SYN-CFG-LG-A."
            ),
            keywords=["door", "proximity", "fault isolation", "TSM", "ATA 52"],
        ),
        _doc(
            document_id="SYN-CDL-PANEL-FAIRING",
            evidence_id="EV-SYN-CDL-PANEL-FAIRING-53-20",
            document_type="CDL",
            title="Synthetic A320 CDL - Access Panel Fairing",
            reference_number="SYN-CDL-PANEL-FAIRING",
            canonical_reference="SYN-CDL-53-20-PANEL",
            revision_id="R1",
            revision_date="2026-04-18",
            ata_chapter="53",
            section_id="CDL-53-20-PANEL",
            quoted_span=(
                "For a synthetic access panel fairing discrepancy, check configuration "
                "SYN-CFG-LG-A effectivity and prepare the cited package for human review."
            ),
            content=(
                "Access panel fairing discrepancy. CDL context applies to A320 "
                "SYN-CFG-LG-A and is controlled benchmark evidence."
            ),
            keywords=["access panel", "fairing", "CDL", "ATA 53"],
        ),
        _doc(
            document_id="SYN-ENG-PROC-FCTL-TRIM",
            evidence_id="EV-SYN-ENG-PROC-FCTL-TRIM-27-00",
            document_type="ENGINEERING_PROCEDURE",
            title="Synthetic Engineering Procedure - Flight Control Trim Review",
            reference_number="SYN-ENG-PROC-FCTL-TRIM",
            canonical_reference="SYN-ENG-27-00-FCTL-TRIM",
            revision_id="R4",
            revision_date="2026-06-03",
            ata_chapter="27",
            section_id="ENG-27-00-FCTL-TRIM",
            quoted_span=(
                "For flight control trim message review, collect current manual references and "
                "route the package to an authorized reviewer; this procedure is not an "
                "approval for dispatch."
            ),
            content=(
                "Flight control trim message review procedure. Collect current evidence "
                "and route to authorized human review."
            ),
            keywords=["flight control", "trim", "engineering procedure", "ATA 27"],
        ),
        _doc(
            document_id="SYN-MEL-HYD-A",
            evidence_id="EV-SYN-MEL-HYD-A-29-01",
            document_type="MEL",
            title="Synthetic A320 MEL - Hydraulic Indication A",
            reference_number="SYN-MEL-HYD-A",
            canonical_reference="SYN-MEL-29-01-HYD",
            revision_id="R1",
            revision_date="2026-06-01",
            ata_chapter="29",
            section_id="MEL-29-01-HYD-A",
            quoted_span=(
                "Synthetic hydraulic low pressure indication condition A requires a current "
                "hydraulic evidence package before authorized review."
            ),
            content="Hydraulic low pressure indication conflict benchmark condition A.",
            keywords=["hydraulic", "low pressure", "MEL", "conflict", "ATA 29"],
        ),
        _doc(
            document_id="SYN-MEL-HYD-B",
            evidence_id="EV-SYN-MEL-HYD-B-29-01",
            document_type="MEL",
            title="Synthetic A320 MEL - Hydraulic Indication B",
            reference_number="SYN-MEL-HYD-B",
            canonical_reference="SYN-MEL-29-01-HYD",
            revision_id="R2",
            revision_date="2026-06-02",
            ata_chapter="29",
            section_id="MEL-29-01-HYD-B",
            quoted_span=(
                "Synthetic hydraulic low pressure indication condition B intentionally "
                "conflicts with another current benchmark revision."
            ),
            content="Hydraulic low pressure indication conflict benchmark condition B.",
            keywords=["hydraulic", "low pressure", "MEL", "conflict", "ATA 29"],
        ),
        _doc(
            document_id="SYN-AMM-UNVERIFIED",
            evidence_id="EV-SYN-AMM-UNVERIFIED-32-99",
            document_type="AMM",
            title="Synthetic Unverified AMM - Landing Gear Sensor",
            reference_number="SYN-AMM-UNVERIFIED",
            canonical_reference="SYN-AMM-32-99-UNVERIFIED",
            revision_id="R1",
            revision_date="2026-06-12",
            approval_status="UNVERIFIED",
            ata_chapter="32",
            section_id="AMM-32-99-UNVERIFIED",
            quoted_span=(
                "Unverified synthetic landing gear sensor note retained for approval gating."
            ),
            content="Unverified landing gear sensor evidence must be rejected by approval gate.",
            keywords=["landing gear", "sensor", "unverified", "AMM", "ATA 32"],
        ),
        _doc(
            document_id="SYN-HIST-GALLEY-001",
            evidence_id="EV-SYN-HIST-GALLEY-001",
            document_type="HISTORICAL_RECORD",
            title="Synthetic Historical Case - Galley Nuisance Message",
            reference_number="SYN-HIST-GALLEY-001",
            canonical_reference="SYN-HIST-GALLEY-001",
            revision_id="V1",
            revision_date="2026-02-02",
            source_authority="HISTORICAL_CONTEXT",
            ata_chapter="25",
            section_id="CASE-GALLEY-001",
            quoted_span=(
                "A previous synthetic galley nuisance message case is historical context only "
                "and cannot support an authoritative technical claim."
            ),
            content="Galley nuisance message historical context only.",
            keywords=["galley", "nuisance", "historical", "ATA 25"],
        ),
    ]
    payload["documents"].extend(additions)
    return payload


def _case(
    case_id: str,
    *,
    aircraft_type: str = "A320",
    configuration: str | None = "SYN-CFG-LG-A",
    ata_chapter: str = "32",
    defect_description: str,
    entered_references: list[str],
    expected_final_state: str,
    expected_references: list[str] | None = None,
    expected_rejected_evidence: list[str] | None = None,
    settings_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    input_case = {
        "case_id": case_id,
        "aircraft_registration": f"SYN-{case_id[-3:]}",
        "aircraft_type": aircraft_type,
        "fleet_or_variant": "SYN-A320-DEMO",
        "configuration": {"profile": configuration} if configuration else None,
        "ata_chapter": ata_chapter,
        "defect_description": defect_description,
        "reported_symptoms": [defect_description],
        "flight_phase_or_context": "synthetic benchmark scenario",
        "entered_references": entered_references,
        "created_by": "synthetic-benchmark",
        "synthetic": True,
    }
    return {
        "case_id": case_id,
        "synthetic": True,
        "input_case": input_case,
        "expected_final_state": expected_final_state,
        "expected_references": expected_references or [],
        "expected_rejected_evidence": expected_rejected_evidence or [],
        "expected_cross_references": [],
        "expected_conflicts": [],
        "golden_claims": [],
        "source_snapshot_id": "synthetic-snapshot-aabw-benchmark-2026-07-12-v1",
        **({"settings_overrides": settings_overrides} if settings_overrides else {}),
    }


def build_benchmark_cases() -> list[dict[str, Any]]:
    return [
        _case(
            "BM-READY-LG-001",
            defect_description=(
                "Landing gear green indication is intermittent after gear extension."
            ),
            entered_references=["SYN-MEL-CURRENT", "SYN-AMM-LINKED-CHECK"],
            expected_final_state="REVIEW_READY",
            expected_references=["SYN-MEL-CURRENT", "SYN-AMM-LINKED-CHECK"],
            expected_rejected_evidence=[
                "EV-SYN-MEL-SUPERSEDED-32-01",
                "EV-SYN-AMM-WRONG-EFFECTIVITY-32-31",
                "EV-SYN-MEL-REJECTED-32-01",
            ],
        ),
        _case(
            "BM-CLARIFY-MISSING-001",
            aircraft_type="",
            configuration=None,
            defect_description=(
                "Landing gear green indication is intermittent after gear extension."
            ),
            entered_references=["SYN-MEL-CURRENT"],
            expected_final_state="NEEDS_CLARIFICATION",
        ),
        _case(
            "BM-SUPERSEDED-REF-001",
            defect_description="Landing gear green indication with old MEL reference entered.",
            entered_references=["SYN-MEL-SUPERSEDED"],
            expected_final_state="NEEDS_CLARIFICATION",
        ),
        _case(
            "BM-WRONG-CONFIG-001",
            configuration="SYN-CFG-LG-B",
            defect_description=(
                "Landing gear green indication is intermittent after gear extension."
            ),
            entered_references=["SYN-MEL-CURRENT"],
            expected_final_state="ABSTAINED",
            expected_rejected_evidence=[
                "EV-SYN-MEL-CURRENT-32-01",
                "EV-SYN-AMM-LINKED-CHECK-32-31",
            ],
        ),
        _case(
            "BM-UNRESOLVED-XREF-001",
            defect_description=(
                "Landing gear indication defect with an entered reference whose mandatory "
                "linked task is unavailable."
            ),
            entered_references=["SYN-MEL-UNRESOLVED-XREF"],
            expected_final_state="ABSTAINED",
            expected_references=["SYN-MEL-UNRESOLVED-XREF"],
        ),
        _case(
            "BM-CONFLICT-HYD-001",
            ata_chapter="29",
            defect_description="Hydraulic low pressure indication conflict benchmark.",
            entered_references=["SYN-MEL-HYD-A"],
            expected_final_state="ESCALATED",
            expected_references=["SYN-MEL-HYD-A", "SYN-MEL-HYD-B"],
        ),
        _case(
            "BM-UNVERIFIED-SOURCE-001",
            defect_description="Landing gear sensor note from unverified AMM source.",
            entered_references=["SYN-AMM-UNVERIFIED"],
            expected_final_state="ABSTAINED",
            expected_rejected_evidence=["EV-SYN-AMM-UNVERIFIED-32-99"],
        ),
        _case(
            "BM-HISTORICAL-ONLY-001",
            ata_chapter="25",
            defect_description="Galley nuisance message with only historical context.",
            entered_references=["SYN-HIST-GALLEY-001"],
            expected_final_state="ABSTAINED",
        ),
        _case(
            "BM-TSM-SUPPORTED-001",
            ata_chapter="52",
            defect_description="Intermittent passenger door proximity message.",
            entered_references=["SYN-TSM-DOOR-FAULT"],
            expected_final_state="REVIEW_READY",
            expected_references=["SYN-TSM-DOOR-FAULT"],
        ),
        _case(
            "BM-CDL-SUPPORTED-001",
            ata_chapter="53",
            defect_description="Access panel fairing discrepancy needs controlled evidence.",
            entered_references=["SYN-CDL-PANEL-FAIRING"],
            expected_final_state="REVIEW_READY",
            expected_references=["SYN-CDL-PANEL-FAIRING"],
        ),
        _case(
            "BM-PROC-SUPPORTED-001",
            ata_chapter="27",
            defect_description="Flight control trim message review procedure package.",
            entered_references=["SYN-ENG-PROC-FCTL-TRIM"],
            expected_final_state="REVIEW_READY",
            expected_references=["SYN-ENG-PROC-FCTL-TRIM"],
        ),
        _case(
            "BM-TOOL-BUDGET-001",
            defect_description=(
                "Landing gear green indication is intermittent after gear extension."
            ),
            entered_references=["SYN-MEL-CURRENT", "SYN-AMM-LINKED-CHECK"],
            expected_final_state="ABSTAINED",
            settings_overrides={"max_tool_calls": 2, "max_graph_steps": 39},
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )


def generate(corpus_out: Path, cases_out: Path) -> dict[str, Any]:
    corpus = build_benchmark_corpus()
    corpus_out.parent.mkdir(parents=True, exist_ok=True)
    corpus_out.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    # Validate before writing cases so failures are loud and early.
    SyntheticCorpus(corpus_out)
    cases = build_benchmark_cases()
    write_jsonl(cases_out, cases)
    return {
        "corpus": str(corpus_out),
        "cases": str(cases_out),
        "documents": len(corpus["documents"]),
        "cases_count": len(cases),
        "source_snapshot_id": corpus["source_snapshot_id"],
        "synthetic": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate AABW synthetic benchmark data")
    parser.add_argument("--corpus-out", type=Path, default=DEFAULT_CORPUS_OUT)
    parser.add_argument("--cases-out", type=Path, default=DEFAULT_CASES_OUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = generate(args.corpus_out, args.cases_out)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
