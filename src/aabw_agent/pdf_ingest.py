"""PDF ingestion helper for creating a controlled demo corpus snapshot.

This script is intentionally conservative. It extracts page text from an explicitly
provided PDF and combines it with a human-supplied manifest. The LLM never assigns
approval, currentness, effectivity, or source authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader

_REFERENCE_RE = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+){2,}\b")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-")
    return cleaned.upper() or "DOC"


def _load_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "document_id",
        "document_type",
        "title",
        "reference_number",
        "revision_id",
        "approval_status",
        "aircraft_types",
        "configurations",
        "source_repository",
        "synthetic",
    ]
    missing = [field for field in required if field not in manifest]
    if missing:
        raise ValueError(f"manifest missing required fields: {', '.join(missing)}")
    if manifest["synthetic"] is not True:
        raise ValueError("hackathon ingest requires synthetic=true unless explicitly authorized")
    return manifest


def build_corpus_from_pdf(pdf_path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    pdf_bytes = pdf_path.read_bytes()
    pdf_hash = _sha256_bytes(pdf_bytes)
    reader = PdfReader(str(pdf_path))
    base_id = _slug(str(manifest["document_id"]))
    now = datetime.now(UTC).date().isoformat()
    documents: list[dict[str, Any]] = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        refs = sorted(set(_REFERENCE_RE.findall(text)))
        document_id = f"{base_id}-P{page_index:03d}"
        evidence_id = f"EV-{document_id}"
        section_id = str(manifest.get("section_prefix") or manifest["reference_number"])
        chunk_hash = _sha256_bytes(f"{pdf_hash}:{page_index}:{text}".encode())
        documents.append(
            {
                "document_id": document_id,
                "evidence_id": evidence_id,
                "document_type": manifest["document_type"],
                "title": manifest["title"],
                "reference_number": manifest["reference_number"],
                "canonical_reference": manifest.get(
                    "canonical_reference", manifest["reference_number"]
                ),
                "revision_id": manifest["revision_id"],
                "revision_date": manifest.get("revision_date") or now,
                "supersedes_revision": manifest.get("supersedes_revision"),
                "revision_status": manifest.get("revision_status", "CURRENT"),
                "approval_status": manifest["approval_status"],
                "source_authority": manifest.get("source_authority", "AUTHORITATIVE"),
                "aircraft_types": manifest["aircraft_types"],
                "configurations": manifest["configurations"],
                "effectivity": manifest.get(
                    "effectivity",
                    {
                        "aircraft_types": manifest["aircraft_types"],
                        "configurations": manifest["configurations"],
                    },
                ),
                "applicability_status": manifest.get("applicability_status", "UNKNOWN"),
                "ata_chapter": str(manifest.get("ata_chapter") or ""),
                "section_id": f"{section_id}-PAGE-{page_index}",
                "page_or_location": f"{pdf_path.name}, page {page_index}",
                "quoted_span": text[:900],
                "content": text,
                "keywords": manifest.get("keywords", []) + refs,
                "cross_references": [
                    {
                        "reference_type": "DOCUMENT_REFERENCE",
                        "target_reference": ref,
                        "mandatory": False,
                    }
                    for ref in refs
                    if ref != manifest["reference_number"]
                ],
                "source_repository": manifest["source_repository"],
                "source_uri": manifest.get("source_uri") or str(pdf_path),
                "source_hash": chunk_hash,
                "synthetic": True,
            }
        )
    if not documents:
        raise ValueError("PDF did not produce any text-bearing pages")
    digest_rows = [
        (
            item["document_id"],
            item["revision_id"],
            item["source_hash"],
            item["approval_status"],
        )
        for item in documents
    ]
    source_snapshot_id = "pdf-snapshot-" + hashlib.sha256(
        json.dumps(sorted(digest_rows), separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "schema_version": "1.0.0",
        "corpus_id": manifest.get("corpus_id", f"pdf-corpus-{base_id.lower()}"),
        "source_snapshot_id": source_snapshot_id,
        "synthetic": True,
        "operational_use_prohibited": True,
        "notice": (
            "SYNTHETIC OR AUTHORIZED DEMO DATA ONLY. NOT FOR OPERATIONAL, "
            "AIRWORTHINESS, DISPATCH, OR RELEASE-TO-SERVICE DECISIONS."
        ),
        "documents": documents,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest one PDF into a controlled demo corpus")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/ingested_corpus.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    corpus = build_corpus_from_pdf(args.pdf, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "documents": len(corpus["documents"]),
                "source_snapshot_id": corpus["source_snapshot_id"],
                "synthetic": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

