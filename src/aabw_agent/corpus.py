"""Read-only, deterministic access to the synthetic demo corpus.

This module intentionally does not use an embedding service.  The demo corpus must
remain usable when the model endpoint is unavailable, so both retrieval strategies
are small deterministic ranking functions over the versioned JSON snapshot.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .ingestion import SourceSnapshotManifest

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.IGNORECASE)
_REQUIRED_DOCUMENT_FIELDS = {
    "document_id": str,
    "evidence_id": str,
    "document_type": str,
    "title": str,
    "reference_number": str,
    "canonical_reference": str,
    "revision_id": str,
    "revision_date": str,
    "revision_status": str,
    "approval_status": str,
    "source_authority": str,
    "aircraft_types": list,
    "configurations": list,
    "effectivity": dict,
    "applicability_status": str,
    "ata_chapter": str,
    "section_id": str,
    "quoted_span": str,
    "content": str,
    "keywords": list,
    "cross_references": list,
    "source_uri": str,
    "source_hash": str,
    "synthetic": bool,
}


class CorpusValidationError(ValueError):
    """Raised when a corpus snapshot violates the demo corpus contract."""


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return deepcopy(value)


def _tokens(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        text = " ".join(str(item) for item in value.values())
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value)
    return [match.group(0).lower() for match in _TOKEN_RE.finditer(text)]


def _normalise_relation(value: str) -> str:
    return value.strip().upper().replace("-", "_").replace(" ", "_")


class SyntheticCorpus:
    """Validated, immutable in-memory view of one synthetic corpus snapshot.

    All public results are new dictionaries. Mutating a returned value can never
    alter later retrieval results or the loaded snapshot.
    """

    DEFAULT_TOP_K = 13

    def __init__(self, path: str | Path | None = None) -> None:
        corpus_path = Path(path) if path is not None else self.default_path()
        try:
            payload = json.loads(corpus_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CorpusValidationError(f"Cannot load corpus {corpus_path}: {exc}") from exc

        self._validate_payload(payload)
        self._path = corpus_path.resolve()
        self._payload = _freeze(payload)
        self._documents = tuple(self._payload["documents"])
        self._by_document_id = {doc["document_id"]: doc for doc in self._documents}
        self._by_evidence_id = {doc["evidence_id"]: doc for doc in self._documents}

    @staticmethod
    def default_path() -> Path:
        return Path(__file__).resolve().parents[2] / "data" / "synthetic_corpus.json"

    @property
    def path(self) -> Path:
        return self._path

    @property
    def corpus_id(self) -> str:
        return self._payload["corpus_id"]

    @property
    def source_snapshot_id(self) -> str:
        return self._payload["source_snapshot_id"]

    @property
    def schema_version(self) -> str:
        return self._payload["schema_version"]

    @property
    def documents(self) -> tuple[dict[str, Any], ...]:
        return tuple(_thaw(doc) for doc in self._documents)

    @property
    def snapshot_manifest(self) -> SourceSnapshotManifest:
        """Typed ingestion handoff pinned to this immutable retrieval snapshot."""
        return SourceSnapshotManifest.from_documents(
            source_snapshot_id=self.source_snapshot_id,
            corpus_id=self.corpus_id,
            schema_version=self.schema_version,
            documents=self.documents,
            synthetic=True,
        )

    @classmethod
    def _validate_payload(cls, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise CorpusValidationError("Corpus root must be an object")
        for field in ("schema_version", "corpus_id", "source_snapshot_id", "notice"):
            if not isinstance(payload.get(field), str) or not payload[field].strip():
                raise CorpusValidationError(f"Corpus field {field!r} must be a non-empty string")
        if payload.get("synthetic") is not True:
            raise CorpusValidationError("Only a synthetic corpus may be loaded")
        if payload.get("operational_use_prohibited") is not True:
            raise CorpusValidationError("Corpus must prohibit operational use")
        documents = payload.get("documents")
        if not isinstance(documents, list) or not documents:
            raise CorpusValidationError("Corpus documents must be a non-empty list")

        document_ids: set[str] = set()
        evidence_ids: set[str] = set()
        for index, document in enumerate(documents):
            cls._validate_document(document, index)
            document_id = document["document_id"]
            evidence_id = document["evidence_id"]
            if document_id in document_ids:
                raise CorpusValidationError(f"Duplicate document_id {document_id!r}")
            if evidence_id in evidence_ids:
                raise CorpusValidationError(f"Duplicate evidence_id {evidence_id!r}")
            document_ids.add(document_id)
            evidence_ids.add(evidence_id)

    @staticmethod
    def _validate_document(document: Any, index: int) -> None:
        prefix = f"documents[{index}]"
        if not isinstance(document, dict):
            raise CorpusValidationError(f"{prefix} must be an object")
        for field, expected_type in _REQUIRED_DOCUMENT_FIELDS.items():
            value = document.get(field)
            if not isinstance(value, expected_type):
                raise CorpusValidationError(f"{prefix}.{field} must be {expected_type.__name__}")
            if expected_type is str and not value.strip():
                raise CorpusValidationError(f"{prefix}.{field} must not be empty")
        if document["synthetic"] is not True:
            raise CorpusValidationError(f"{prefix}.synthetic must be true")
        try:
            date.fromisoformat(document["revision_date"])
        except ValueError as exc:
            raise CorpusValidationError(f"{prefix}.revision_date must be ISO-8601") from exc
        for field in ("aircraft_types", "configurations", "keywords"):
            if not all(isinstance(item, str) and item.strip() for item in document[field]):
                raise CorpusValidationError(f"{prefix}.{field} must contain strings")
        for ref_index, reference in enumerate(document["cross_references"]):
            if not isinstance(reference, dict):
                raise CorpusValidationError(
                    f"{prefix}.cross_references[{ref_index}] must be an object"
                )
            if not isinstance(reference.get("target_reference"), str):
                raise CorpusValidationError(
                    f"{prefix}.cross_references[{ref_index}].target_reference must be a string"
                )
            if not isinstance(reference.get("mandatory"), bool):
                raise CorpusValidationError(
                    f"{prefix}.cross_references[{ref_index}].mandatory must be boolean"
                )

    @staticmethod
    def _checked_top_k(top_k: int) -> int:
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
            raise ValueError("top_k must be a non-negative integer")
        return top_k

    @staticmethod
    def _document_text(document: Mapping[str, Any]) -> str:
        fields = (
            document["title"],
            document["reference_number"],
            document["canonical_reference"],
            document["section_id"],
            document["quoted_span"],
            document["content"],
            " ".join(document["keywords"]),
        )
        return " ".join(fields).lower()

    @staticmethod
    def _filter_value(document: Mapping[str, Any], key: str) -> Any:
        aliases = {
            "aircraft_type": "aircraft_types",
            "configuration": "configurations",
            "reference": "reference_number",
        }
        path = aliases.get(key, key).split(".")
        value: Any = document
        for component in path:
            if not isinstance(value, Mapping) or component not in value:
                return None
            value = value[component]
        return value

    @classmethod
    def _matches_filters(
        cls, document: Mapping[str, Any], filters: Mapping[str, Any] | None
    ) -> bool:
        if not filters:
            return True
        if not isinstance(filters, Mapping):
            raise TypeError("filters must be a mapping")
        for key, expected in filters.items():
            if expected is None:
                continue
            actual = cls._filter_value(document, str(key))
            expected_values = (
                list(expected)
                if isinstance(expected, Sequence) and not isinstance(expected, (str, bytes))
                else [expected]
            )
            if isinstance(actual, Sequence) and not isinstance(actual, (str, bytes)):
                if not any(item in actual for item in expected_values):
                    return False
            elif actual not in expected_values:
                return False
        return True

    @staticmethod
    def _with_score(document: Mapping[str, Any], score_name: str, score: float) -> dict[str, Any]:
        result = _thaw(document)
        result["retrieval_scores"] = {score_name: round(float(score), 6)}
        return result

    def search_semantic(
        self,
        query: str,
        filters: Mapping[str, Any] | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:
        """Rank by deterministic cosine similarity over corpus text tokens."""

        limit = self._checked_top_k(top_k)
        query_counter = Counter(_tokens(query))
        if not query_counter or limit == 0:
            return []
        query_norm = math.sqrt(sum(count * count for count in query_counter.values()))
        ranked: list[tuple[float, str, Mapping[str, Any]]] = []
        query_phrase = str(query).strip().lower()
        for document in self._documents:
            if not self._matches_filters(document, filters):
                continue
            text = self._document_text(document)
            doc_counter = Counter(_tokens(text))
            dot = sum(count * doc_counter[token] for token, count in query_counter.items())
            if dot == 0:
                continue
            doc_norm = math.sqrt(sum(count * count for count in doc_counter.values()))
            score = dot / (query_norm * doc_norm)
            if query_phrase and query_phrase in text:
                score += 0.1
            # Current material wins close retrieval ties without hiding stale fixtures.
            # Revision/applicability gates remain responsible for actual acceptance.
            if document["revision_status"] == "CURRENT":
                score += 0.05
            ranked.append((score, document["document_id"], document))
        ranked.sort(key=lambda row: (-row[0], row[1]))
        return [self._with_score(doc, "semantic", score) for score, _, doc in ranked[:limit]]

    def search_lexical(
        self,
        query: str,
        filters: Mapping[str, Any] | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:
        """Rank exact token/phrase matches; stable across processes and machines."""

        limit = self._checked_top_k(top_k)
        query_tokens = _tokens(query)
        if not query_tokens or limit == 0:
            return []
        unique_query = set(query_tokens)
        query_phrase = str(query).strip().lower()
        ranked: list[tuple[float, str, Mapping[str, Any]]] = []
        for document in self._documents:
            if not self._matches_filters(document, filters):
                continue
            text = self._document_text(document)
            doc_counts = Counter(_tokens(text))
            matched = sum(1 for token in unique_query if doc_counts[token])
            if matched == 0:
                continue
            coverage = matched / len(unique_query)
            frequency = sum(min(doc_counts[token], 3) for token in unique_query) / (
                3 * len(unique_query)
            )
            phrase_bonus = 0.25 if query_phrase and query_phrase in text else 0.0
            score = coverage + 0.2 * frequency + phrase_bonus
            ranked.append((score, document["document_id"], document))
        ranked.sort(key=lambda row: (-row[0], row[1]))
        return [self._with_score(doc, "lexical", score) for score, _, doc in ranked[:limit]]

    def lookup_document(
        self, reference_number: str, revision_id: str | None = None
    ) -> dict[str, Any] | None:
        """Resolve document, evidence, canonical, or source reference exactly."""

        target = str(reference_number).strip().casefold()
        if not target:
            return None
        matches = [
            document
            for document in self._documents
            if target
            in {
                document["reference_number"].casefold(),
                document["canonical_reference"].casefold(),
                document["document_id"].casefold(),
                document["evidence_id"].casefold(),
            }
            and (revision_id is None or document["revision_id"] == revision_id)
        ]
        if not matches:
            return None
        matches.sort(
            key=lambda doc: (
                doc["revision_status"] == "CURRENT",
                doc["revision_date"],
                doc["revision_id"],
                doc["document_id"],
            ),
            reverse=True,
        )
        return self._with_score(matches[0], "exact", 1.0)

    def get_revision_chain(self, document_id: str) -> list[dict[str, Any]]:
        seed = self._find_internal(document_id)
        if seed is None:
            return []
        chain = [
            document
            for document in self._documents
            if document["canonical_reference"] == seed["canonical_reference"]
        ]
        chain.sort(
            key=lambda doc: (doc["revision_date"], doc["revision_id"], doc["document_id"]),
            reverse=True,
        )
        return [_thaw(document) for document in chain]

    def _find_internal(self, node_id: str) -> Mapping[str, Any] | None:
        if node_id in self._by_document_id:
            return self._by_document_id[node_id]
        if node_id in self._by_evidence_id:
            return self._by_evidence_id[node_id]
        found = self.lookup_document(node_id)
        return self._by_document_id.get(found["document_id"]) if found else None

    def resolve_cross_reference(
        self, reference: str | Mapping[str, Any], source_context: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        del source_context  # Resolution is exact; applicability is a separate deterministic gate.
        if isinstance(reference, Mapping):
            target_reference = str(
                reference.get("target_reference") or reference.get("reference_number") or ""
            ).strip()
        else:
            target_reference = str(reference).strip()
        evidence = self.lookup_document(target_reference)
        return {
            "status": "RESOLVED" if evidence is not None else "NOT_IN_CORPUS",
            "target_reference": target_reference,
            "evidence": evidence,
        }

    def traverse_evidence_graph(
        self,
        node_id: str,
        relation_types: Sequence[str] | None = None,
        depth: int = 1,
    ) -> list[dict[str, Any]]:
        """Breadth-first graph traversal with cycle and depth guards."""

        if isinstance(depth, bool) or not isinstance(depth, int) or not 0 <= depth <= 10:
            raise ValueError("depth must be an integer from 0 to 10")
        start = self._find_internal(node_id)
        if start is None or depth == 0:
            return []
        allowed = (
            {_normalise_relation(item) for item in relation_types}
            if relation_types
            else {"CROSS_REFERENCE", "SUPERSEDES", "SUPERSEDED_BY"}
        )
        aliases = {"XREF": "CROSS_REFERENCE", "CROSS_REFERENCES": "CROSS_REFERENCE"}
        allowed = {aliases.get(item, item) for item in allowed}
        visited = {start["document_id"]}
        queue: deque[tuple[Mapping[str, Any], int]] = deque([(start, 0)])
        found: list[tuple[Mapping[str, Any], int, str]] = []

        while queue:
            document, distance = queue.popleft()
            if distance >= depth:
                continue
            neighbours: list[tuple[Mapping[str, Any], str]] = []
            if "CROSS_REFERENCE" in allowed:
                for reference in document["cross_references"]:
                    target = self._find_internal(reference["target_reference"])
                    if target is not None:
                        neighbours.append((target, "CROSS_REFERENCE"))
            if "SUPERSEDES" in allowed and document.get("supersedes_revision"):
                for candidate in self._documents:
                    if (
                        candidate["canonical_reference"] == document["canonical_reference"]
                        and candidate["revision_id"] == document["supersedes_revision"]
                    ):
                        neighbours.append((candidate, "SUPERSEDES"))
            if "SUPERSEDED_BY" in allowed:
                for candidate in self._documents:
                    if (
                        candidate["canonical_reference"] == document["canonical_reference"]
                        and candidate.get("supersedes_revision") == document["revision_id"]
                    ):
                        neighbours.append((candidate, "SUPERSEDED_BY"))
            neighbours.sort(key=lambda item: (item[0]["document_id"], item[1]))
            for neighbour, relation in neighbours:
                neighbour_id = neighbour["document_id"]
                if neighbour_id in visited:
                    continue
                visited.add(neighbour_id)
                next_distance = distance + 1
                found.append((neighbour, next_distance, relation))
                queue.append((neighbour, next_distance))

        results: list[dict[str, Any]] = []
        for document, distance, relation in found:
            result = self._with_score(document, "graph", 1.0 / distance)
            result["graph"] = {"depth": distance, "relation": relation}
            results.append(result)
        return results

    def search_historical_cases(
        self,
        case_features: Mapping[str, Any] | str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:
        limit = self._checked_top_k(top_k)
        query_tokens = set(_tokens(case_features))
        if not query_tokens or limit == 0:
            return []
        ranked: list[tuple[float, str, Mapping[str, Any]]] = []
        for document in self._documents:
            if document["document_type"] != "HISTORICAL_RECORD":
                continue
            candidate_tokens = set(
                _tokens(document.get("case_features", {})) + _tokens(self._document_text(document))
            )
            intersection = len(query_tokens & candidate_tokens)
            if intersection == 0:
                continue
            union = len(query_tokens | candidate_tokens)
            score = intersection / union
            ranked.append((score, document["document_id"], document))
        ranked.sort(key=lambda row: (-row[0], row[1]))
        return [self._with_score(doc, "historical", score) for score, _, doc in ranked[:limit]]


__all__ = ["CorpusValidationError", "SyntheticCorpus"]
