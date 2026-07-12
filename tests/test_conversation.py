from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aabw_agent.api import _workflow_response
from aabw_agent.config import Settings
from aabw_agent.conversation import ConversationCoordinator, build_user_answer
from aabw_agent.corpus import SyntheticCorpus
from aabw_agent.workflow import WorkflowRunner


def test_custom_chat_case_collects_choices_then_runs_full_workflow(
    offline_settings, tmp_path: Path
) -> None:
    coordinator = ConversationCoordinator(SyntheticCorpus(offline_settings.corpus_path))
    session = coordinator.start_session(
        " ".join(
            [
                "I'm not a maintenance engineer.",
                "The landing gear green light flickers after extension",
                "and the note mentions SYN-MEL-CURRENT.",
            ]
        )
    )

    first_turn = coordinator.continue_session(session)
    assert first_turn["status"] == "needs_clarification"
    assert first_turn["clarification"]["field"] == "aircraft_type"

    second_turn = coordinator.continue_session(session, choice_value="A320")
    assert second_turn["status"] == "needs_clarification"
    assert second_turn["clarification"]["field"] == "configuration"

    ready_turn = coordinator.continue_session(session, choice_value="SYN-CFG-LG-A")
    assert ready_turn["status"] == "ready"
    assert ready_turn["case"]["case_id"].startswith("CHAT-")
    assert ready_turn["case"]["case_id"] not in {
        "BM-READY-LG-001",
        "EVAL-READY-001",
    }

    result = WorkflowRunner(settings=offline_settings).run(ready_turn["case"])
    trace = Path(result["trace_context"]["local_trace_path"])
    records = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    tool_actors = {
        record["actor"]
        for record in records
        if record["event_type"] == "tool"
    }

    assert result["final_state"] == "REVIEW_READY"
    assert result["gate_results"]["applicability"] == "PASS"
    assert result["gate_results"]["approval"] == "PASS"
    assert result["gate_results"]["revision"] == "PASS"
    assert result["gate_results"]["cross_reference"] == "COMPLETE"
    assert result["gate_results"]["conflict"] == "PASS"
    assert {
        "query_expansion_agent",
        "revision_temporal_agent",
        "keyword_metadata_agent",
        "cross_reference_graph_agent",
        "historical_context_agent",
    } <= tool_actors


def test_non_professional_answer_gives_final_next_step_and_exact_citations(
    offline_settings, tmp_path: Path
) -> None:
    coordinator = ConversationCoordinator(SyntheticCorpus(offline_settings.corpus_path))
    session = coordinator.start_session(_non_professional_question())
    coordinator.continue_session(session)
    coordinator.continue_session(session, choice_value="A320")
    ready_turn = coordinator.continue_session(session, choice_value="SYN-CFG-LG-A")
    result = WorkflowRunner(settings=offline_settings).run(ready_turn["case"])

    answer = build_user_answer(result)

    assert answer.startswith("Final answer:")
    assert "Do not troubleshoot the aircraft yourself" in answer
    assert "Fix path for authorized maintenance:" in answer
    assert "use SYN-AMM-LINKED-CHECK" in answer
    assert "controlled source" in answer
    assert "Ask authorized maintenance personnel" in answer
    assert "SYN-AMM-LINKED-CHECK" in answer
    assert "Citations:" in answer
    assert "SYN-MEL-UNRESOLVED-XREF" not in answer
    assert (
        "SYN-MEL-CURRENT: For intermittent landing gear green indication after gear extension, "
        "record the indication defect and perform the mandatory linked operational check in "
        "SYN-AMM-LINKED-CHECK before preparing the evidence package for authorized review."
    ) in answer
    assert (
        "SYN-AMM-LINKED-CHECK: Perform the synthetic landing gear indication operational check "
        "for configuration SYN-CFG-LG-A. Confirm indication behavior through the prescribed "
        "test sequence and record observed results for authorized human review."
    ) in answer


def test_chat_response_exposes_exact_citation_content_subagents_and_logs(
    offline_settings: Settings,
) -> None:
    result = WorkflowRunner(settings=offline_settings).run(_non_professional_case())
    response = _workflow_response(result, offline_settings, include_events=True)

    citations = {
        item["reference_number"]: item["quoted_span"] for item in response["citations"]
    }
    assert citations["SYN-MEL-CURRENT"] == (
        "For intermittent landing gear green indication after gear extension, record the "
        "indication defect and perform the mandatory linked operational check in "
        "SYN-AMM-LINKED-CHECK before preparing the evidence package for authorized review."
    )
    assert citations["SYN-AMM-LINKED-CHECK"] == (
        "Perform the synthetic landing gear indication operational check for configuration "
        "SYN-CFG-LG-A. Confirm indication behavior through the prescribed test sequence and "
        "record observed results for authorized human review."
    )
    assert "SYN-MEL-UNRESOLVED-XREF" not in citations
    assert "Final answer:" in response["answer"]
    assert "Citations:" in response["answer"]

    agent_events = [
        event
        for event in response["events"]
        if event["event_type"] == "agent" and event["status"] == "START"
    ]
    assert [event["actor"] for event in agent_events] == [
        "query_expansion_agent",
        "revision_temporal_agent",
        "keyword_metadata_agent",
        "cross_reference_graph_agent",
        "historical_context_agent",
    ]
    assert response["tool_calls"]
    assert response["events"][-1]["event_type"] == "terminal"


def _non_professional_question() -> str:
    return " ".join(
        [
            "I'm not a maintenance engineer.",
            "The landing gear green light flickers after extension.",
            "What should I do next?",
        ]
    )


def _non_professional_case() -> dict[str, Any]:
    question = _non_professional_question()
    return {
        "case_id": "CHAT-STATIC-001",
        "aircraft_registration": None,
        "aircraft_type": "A320",
        "fleet_or_variant": "SYN-A320-DEMO",
        "configuration": {"profile": "SYN-CFG-LG-A"},
        "ata_chapter": None,
        "defect_description": question,
        "reported_symptoms": [
            "I'm not a maintenance engineer. The landing gear green light flickers after extension."
        ],
        "flight_phase_or_context": "custom chat intake",
        "entered_references": [],
        "constraints": [],
        "attachments": [],
        "created_by": "chat-user",
        "synthetic": True,
    }
