from __future__ import annotations

import json
from pathlib import Path

from aabw_agent.conversation import ConversationCoordinator
from aabw_agent.corpus import SyntheticCorpus
from aabw_agent.workflow import WorkflowRunner


def test_custom_chat_case_collects_choices_then_runs_full_workflow(
    offline_settings, tmp_path: Path
) -> None:
    coordinator = ConversationCoordinator(SyntheticCorpus(offline_settings.corpus_path))
    session = coordinator.start_session(
        "I'm not a maintenance engineer. The landing gear green light flickers after extension and the note mentions SYN-MEL-CURRENT."
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
