"""Conversational intake helpers for custom non-benchmark cases."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from .corpus import SyntheticCorpus

_REFERENCE_RE = re.compile(r"\bSYN-[A-Z0-9-]+\b", re.IGNORECASE)
_ATA_RE = re.compile(r"\bATA\s*([0-9]{2})\b", re.IGNORECASE)


def _title_case_words(value: str) -> str:
    return " ".join(part.capitalize() for part in value.strip().split())


@dataclass
class ConversationSession:
    session_id: str
    draft_case: dict[str, Any]
    original_question: str
    pending_field: str | None = None
    clarification_count: int = 0
    history: list[dict[str, str]] = field(default_factory=list)


class ConversationCoordinator:
    """Collects a minimum typed case through short clarification turns."""

    def __init__(self, corpus: SyntheticCorpus) -> None:
        self.corpus = corpus
        aircraft_types = {
            aircraft
            for document in corpus.documents
            for aircraft in document.get("aircraft_types", [])
            if aircraft
        }
        self.aircraft_types = sorted(aircraft_types) or ["A320"]
        self.configurations_by_aircraft = self._build_configuration_index()

    def start_session(self, message: str) -> ConversationSession:
        case_id = f"CHAT-{uuid.uuid4().hex[:8].upper()}"
        draft_case = {
            "case_id": case_id,
            "aircraft_registration": None,
            "aircraft_type": "",
            "fleet_or_variant": "SYN-A320-DEMO",
            "configuration": None,
            "ata_chapter": None,
            "defect_description": message.strip(),
            "reported_symptoms": [message.strip()] if message.strip() else [],
            "flight_phase_or_context": "custom chat intake",
            "entered_references": [],
            "constraints": [],
            "attachments": [],
            "created_by": "chat-user",
            "synthetic": True,
        }
        session = ConversationSession(
            session_id=f"session-{uuid.uuid4().hex[:10]}",
            draft_case=draft_case,
            original_question=message.strip(),
        )
        self._apply_freeform_message(session, message)
        return session

    def continue_session(
        self,
        session: ConversationSession,
        *,
        message: str | None = None,
        choice_value: str | None = None,
    ) -> dict[str, Any]:
        if choice_value:
            self._apply_choice(session, choice_value)
            session.history.append({"role": "user", "content": choice_value})
        elif message and message.strip():
            cleaned = message.strip()
            session.history.append({"role": "user", "content": cleaned})
            self._apply_freeform_message(session, cleaned)

        clarification = self._next_clarification(session)
        if clarification is not None:
            session.pending_field = clarification["field"]
            session.clarification_count += 1
            return {
                "status": "needs_clarification",
                "session_id": session.session_id,
                "case_id": session.draft_case["case_id"],
                "draft_case": session.draft_case,
                "clarification": clarification,
            }

        session.pending_field = None
        return {
            "status": "ready",
            "session_id": session.session_id,
            "case_id": session.draft_case["case_id"],
            "case": session.draft_case,
        }

    def _build_configuration_index(self) -> dict[str, list[str]]:
        mapping: dict[str, set[str]] = {}
        for document in self.corpus.documents:
            for aircraft in document.get("aircraft_types", []) or ["A320"]:
                bucket = mapping.setdefault(str(aircraft), set())
                for configuration in document.get("configurations", []):
                    if configuration:
                        bucket.add(str(configuration))
        return {aircraft: sorted(values) for aircraft, values in mapping.items()}

    def _apply_choice(self, session: ConversationSession, choice_value: str) -> None:
        field = session.pending_field
        if field == "aircraft_type":
            session.draft_case["aircraft_type"] = choice_value
            if session.draft_case.get("configuration") is None:
                session.draft_case["configuration"] = None
            return
        if field == "configuration":
            session.draft_case["configuration"] = {"profile": choice_value}
            return
        if field == "entered_reference":
            if choice_value != "NO_REFERENCE":
                references = session.draft_case.setdefault("entered_references", [])
                if choice_value not in references:
                    references.append(choice_value)
            return
        self._apply_freeform_message(session, choice_value)

    def _apply_freeform_message(self, session: ConversationSession, message: str) -> None:
        draft = session.draft_case
        text = message.strip()
        if not text:
            return

        if session.pending_field == "aircraft_type":
            aircraft = self._extract_aircraft_type(text)
            if aircraft:
                draft["aircraft_type"] = aircraft
                return
        if session.pending_field == "configuration":
            configuration = self._extract_configuration(text, draft.get("aircraft_type"))
            if configuration:
                draft["configuration"] = {"profile": configuration}
                return

        if not draft.get("defect_description"):
            draft["defect_description"] = text
        if text not in draft.get("reported_symptoms", []):
            draft.setdefault("reported_symptoms", []).append(text)

        aircraft = self._extract_aircraft_type(text)
        if aircraft:
            draft["aircraft_type"] = aircraft

        configuration = self._extract_configuration(text, draft.get("aircraft_type"))
        if configuration:
            draft["configuration"] = {"profile": configuration}

        ata_match = _ATA_RE.search(text)
        if ata_match:
            draft["ata_chapter"] = ata_match.group(1)

        references = sorted({item.upper() for item in _REFERENCE_RE.findall(text)})
        if references:
            existing = draft.setdefault("entered_references", [])
            for reference in references:
                if reference not in existing:
                    existing.append(reference)

    def _extract_aircraft_type(self, message: str) -> str | None:
        upper = message.upper()
        for aircraft in self.aircraft_types:
            if aircraft.upper() in upper:
                return aircraft
        return None

    def _extract_configuration(self, message: str, aircraft_type: str | None) -> str | None:
        upper = message.upper()
        options = self.configurations_by_aircraft.get(aircraft_type or "", [])
        for configuration in options:
            if configuration.upper() in upper:
                return configuration
        for configuration_list in self.configurations_by_aircraft.values():
            for configuration in configuration_list:
                if configuration.upper() in upper:
                    return configuration
        return None

    def _next_clarification(self, session: ConversationSession) -> dict[str, Any] | None:
        draft = session.draft_case
        if not str(draft.get("aircraft_type") or "").strip():
            return {
                "field": "aircraft_type",
                "question": "Which aircraft family is this closest to?",
                "options": [
                    {
                        "id": f"aircraft-{index}",
                        "label": aircraft,
                        "value": aircraft,
                        "description": "Use this aircraft type for applicability and retrieval.",
                    }
                    for index, aircraft in enumerate(self.aircraft_types, start=1)
                ],
            }

        profile = (draft.get("configuration") or {}).get("profile")
        if not str(profile or "").strip():
            aircraft_type = str(draft.get("aircraft_type"))
            configurations = self.configurations_by_aircraft.get(aircraft_type) or [
                "SYN-CFG-LG-A",
                "SYN-CFG-LG-B",
            ]
            return {
                "field": "configuration",
                "question": "Which configuration profile is the best match?",
                "options": [
                    {
                        "id": f"config-{index}",
                        "label": configuration,
                        "value": configuration,
                        "description": (
                            "Needed to run applicability and effectivity checks in the demo corpus."
                        ),
                    }
                    for index, configuration in enumerate(configurations, start=1)
                ],
            }

        return None


def build_user_answer(result: dict[str, Any]) -> str:
    package = result.get("review_package") or {}
    final_state = result.get("final_state") or "FAILED"
    claim_texts = [claim.get("claim_text") for claim in package.get("claims", []) if claim.get("claim_text")]
    key_points = "; ".join(claim_texts[:3])
    if final_state == "REVIEW_READY":
        summary = package.get("case_summary") or "The case is ready for authorized human review."
        return (
            f"{summary} Final status: {final_state}. "
            f"Key supported points: {key_points or 'Cited evidence is attached below.'}"
        )
    limitations = package.get("limitations", [])
    next_action = package.get("required_human_actions", [])
    return (
        f"Final status: {final_state}. "
        f"Why it stopped: {result.get('route_reason') or 'The evidence gate did not clear.'} "
        f"{' '.join(limitations[:2])} {' '.join(next_action[:1])}".strip()
    )


def prompt_bundle(profile: str) -> dict[str, Any]:
    from .deep_agent import (
        AGENT_SUPERVISOR_INSTRUCTIONS,
        CRITIC_SUBAGENT_PROMPT,
        PROMPT_PROFILE_INSTRUCTIONS,
        RETRIEVAL_SUBAGENT_PROMPT,
        VALIDATION_SUBAGENT_PROMPT,
    )

    return {
        "profile": profile,
        "supervisor": AGENT_SUPERVISOR_INSTRUCTIONS.strip(),
        "retrieval": RETRIEVAL_SUBAGENT_PROMPT.strip(),
        "validation": VALIDATION_SUBAGENT_PROMPT.strip(),
        "critic": CRITIC_SUBAGENT_PROMPT.strip(),
        "profile_instructions": PROMPT_PROFILE_INSTRUCTIONS.get(profile, "").strip(),
    }

