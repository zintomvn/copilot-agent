import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  FileText,
  Loader2,
  MessageSquare,
  Send,
  ShieldCheck,
  User,
  Wrench,
  XCircle
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8002";
const CUSTOM_CASE_ID = "CUSTOM-CHAT";
const BENCHMARK_PROMPT =
  "Analyze BM-READY-LG-001 and show the agent plan, tools, evidence gates, citations, and Langfuse trace.";
const CUSTOM_PROMPT =
  "I'm not a maintenance engineer. The landing gear green light flickers after extension. What should I do next?";

function statusClass(status) {
  if (status === "REVIEW_READY" || status === "PASS" || status === "COMPLETE" || status === "CURRENT" || status === "APPROVED" || status === "RESOLVED") return "ok";
  if (status === "ESCALATED" || status === "FAILED" || status === "FAIL" || status === "SUPERSEDED" || status === "REJECTED" || status === "UNRESOLVED" || status === "NOT_IN_CORPUS") return "bad";
  if (status === "NEEDS_CLARIFICATION" || status === "ABSTAINED" || status === "UNKNOWN" || status === "UNVERIFIED") return "warn";
  return "neutral";
}

function compactEventName(value) {
  return String(value || "").replaceAll("_", " ").toLowerCase();
}

function Message({ message, onChoiceSelect, disabled }) {
  const isUser = message.role === "user";
  const Icon = isUser ? User : message.kind === "tools" ? Wrench : Bot;
  return (
    <article className={`message ${isUser ? "user" : "assistant"} ${message.kind || ""}`}>
      <div className="avatar">
        <Icon size={17} />
      </div>
      <div className="bubble">
        <p>{message.content}</p>
        {message.kind === "clarification" && Array.isArray(message.items) && message.items.length > 0 && (
          <div className="choice-grid">
            {message.items.map((item) => (
              <button
                className="choice-card"
                key={item.id || item.value}
                onClick={() => onChoiceSelect?.(item.value)}
                disabled={disabled}
              >
                <strong>{item.label}</strong>
                <span>{item.description}</span>
              </button>
            ))}
          </div>
        )}
        {message.kind === "tools" && Array.isArray(message.items) && message.items.length > 0 && (
          <details className="inline-details">
            <summary>
              <ChevronDown size={14} />
              <span>Show tools called</span>
            </summary>
            <div className="message-items">
              {message.items.slice(0, 12).map((item, index) => (
                <div className="message-item" key={`${message.kind}-${index}`}>
                  <strong>{item.tool}</strong>
                  <span>{item.actor} / {item.status} / {item.result_count ?? 0} results</span>
                </div>
              ))}
            </div>
          </details>
        )}
        {message.kind === "claims" && Array.isArray(message.items) && message.items.length > 0 && (
          <div className="message-items">
            {message.items.slice(0, 6).map((item, index) => (
              <div className="message-item" key={`${message.kind}-${index}`}>
                <strong>{item.claim_id || `claim ${index + 1}`}</strong>
                <span>{item.claim_text}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}

function StatusCard({ result, health }) {
  const finalState = result?.final_state || "READY";
  const StatusIcon =
    finalState === "REVIEW_READY" ? CheckCircle2 : finalState === "READY" ? MessageSquare : AlertTriangle;
  const gates = result?.gate_results || {};
  return (
    <section className="side-card">
      <div className={`state-card ${statusClass(finalState)}`}>
        <StatusIcon size={20} />
        <div>
          <span>Workflow state</span>
          <strong>{finalState}</strong>
        </div>
      </div>
      <div className="runtime-grid">
        <div>
          <span>Deep Agents</span>
          <strong>{health?.deep_agent_enabled ? "enabled" : "off"}</strong>
        </div>
        <div>
          <span>Langfuse</span>
          <strong>{health?.langfuse_enabled ? "enabled" : "off"}</strong>
        </div>
        <div>
          <span>Run ID</span>
          <strong>{result?.run_id || "not run"}</strong>
        </div>
        <div>
          <span>Case</span>
          <strong>{result?.case_id || "none"}</strong>
        </div>
      </div>
      {result?.langfuse_trace_url && (
        <a className="trace-link" href={result.langfuse_trace_url} target="_blank" rel="noreferrer">
          <ExternalLink size={15} />
          <span>Open Langfuse trace</span>
        </a>
      )}
      <div className="gate-list">
        {["applicability", "revision", "approval", "cross_reference", "conflict", "citation"].map((gate) => (
          <div className={`gate-row ${statusClass(gates[gate])}`} key={gate}>
            <span>{gate.replaceAll("_", " ")}</span>
            <strong>{gates[gate] || "pending"}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function AnswerPanel({ result }) {
  if (!result?.answer) return null;
  return (
    <section className="side-card answer-card">
      <div className="section-title">
        <MessageSquare size={16} />
        <h2>Answer</h2>
      </div>
      <p>{result.answer}</p>
    </section>
  );
}

function CitationsPanel({ result }) {
  const citations = result?.citations || [];
  return (
    <section className="side-card evidence-card">
      <div className="section-title">
        <FileText size={16} />
        <h2>Sources and citations</h2>
      </div>
      <div className="evidence-mini-list">
        {citations.slice(0, 8).map((item) => (
          <div className="evidence-mini" key={item.evidence_id}>
            <strong>{item.reference_number}</strong>
            <span>{item.document_type} / {item.revision_id} / {item.page_or_location}</span>
            <p>{item.quoted_span}</p>
          </div>
        ))}
        {citations.length === 0 && <p className="muted">No citations yet.</p>}
      </div>
    </section>
  );
}

function ChecksPanel({ result }) {
  const pack = result?.review_package || {};
  const applicability = pack.applicability_checks || [];
  const approvals = pack.approval_checks || [];
  const revisions = pack.revision_checks || [];
  const crossReferences = pack.cross_references || [];
  const conflicts = pack.conflicts || [];
  return (
    <section className="side-card checks-card">
      <div className="section-title">
        <ShieldCheck size={16} />
        <h2>Checks</h2>
      </div>
      <div className="check-group">
        <strong>Applicability</strong>
        {applicability.length ? applicability.map((item) => (
          <div className={`check-row ${statusClass(item.status)}`} key={`app-${item.evidence_id}`}>
            <span>{item.evidence_id}</span>
            <strong>{item.status}</strong>
          </div>
        )) : <p className="muted">No applicability checks yet.</p>}
      </div>
      <div className="check-group">
        <strong>Approval</strong>
        {approvals.length ? approvals.map((item) => (
          <div className={`check-row ${statusClass(item.status)}`} key={`approval-${item.evidence_id}`}>
            <span>{item.evidence_id}</span>
            <strong>{item.status}</strong>
          </div>
        )) : <p className="muted">No approval checks yet.</p>}
      </div>
      <div className="check-group">
        <strong>Revision</strong>
        {revisions.length ? revisions.map((item) => (
          <div className={`check-row ${statusClass(item.status)}`} key={`revision-${item.evidence_id}`}>
            <span>{item.evidence_id}</span>
            <strong>{item.status}</strong>
          </div>
        )) : <p className="muted">No revision checks yet.</p>}
      </div>
      <div className="check-group">
        <strong>Cross reference</strong>
        {crossReferences.length ? crossReferences.map((item, index) => (
          <div className={`check-row ${statusClass(item.status)}`} key={`xref-${index}`}>
            <span>{item.target_reference}</span>
            <strong>{item.status}</strong>
          </div>
        )) : <p className="muted">No cross references yet.</p>}
      </div>
      <div className="check-group">
        <strong>Conflict</strong>
        {conflicts.length ? conflicts.map((item) => (
          <div className={`check-row ${statusClass(item.resolution_status === "UNRESOLVED" ? "ESCALATED" : "PASS")}`} key={item.conflict_id}>
            <span>{item.description}</span>
            <strong>{item.resolution_status}</strong>
          </div>
        )) : <p className="muted">No conflicts detected.</p>}
      </div>
    </section>
  );
}

function TracePanel({ result }) {
  const toolCalls = result?.tool_calls || [];
  const events = result?.events || [];
  const nodeEvents = events.filter((event) => event.event_type === "node_start");
  return (
    <section className="side-card trace-card">
      <details>
        <summary className="details-summary">
          <div className="section-title">
            <Wrench size={16} />
            <h2>Tools and trace</h2>
          </div>
          <ChevronDown size={16} />
        </summary>
        <div className="trace-steps">
          {nodeEvents.slice(0, 12).map((event) => (
            <div className="trace-step" key={event.sequence}>
              <span>{event.sequence}</span>
              <div>
                <strong>{event.details?.state_after}</strong>
                <small>{event.actor}</small>
              </div>
            </div>
          ))}
          {nodeEvents.length === 0 && <p className="muted">Run the chat to see workflow nodes.</p>}
        </div>
        <div className="tool-list">
          {toolCalls.slice(0, 12).map((event) => (
            <div className="tool-row" key={`${event.sequence}-${event.actor}`}>
              <strong>{event.details?.tool}</strong>
              <span>{event.actor} / {compactEventName(event.status)} / {event.details?.result_count ?? 0}</span>
            </div>
          ))}
          {toolCalls.length === 0 && <p className="muted">Tool calls will appear here.</p>}
        </div>
      </details>
    </section>
  );
}

function PromptPanel({ result }) {
  const prompts = result?.system_prompts;
  if (!prompts) return null;
  return (
    <section className="side-card prompt-card">
      <details>
        <summary className="details-summary">
          <div className="section-title">
            <Bot size={16} />
            <h2>System prompts</h2>
          </div>
          <ChevronDown size={16} />
        </summary>
        <div className="prompt-stack">
          {[
            ["Prompt profile", prompts.profile_instructions],
            ["Supervisor", prompts.supervisor],
            ["Retrieval", prompts.retrieval],
            ["Validation", prompts.validation],
            ["Critic", prompts.critic]
          ].map(([label, value]) => (
            <div className="prompt-block" key={label}>
              <strong>{label}</strong>
              <p>{value}</p>
            </div>
          ))}
        </div>
      </details>
    </section>
  );
}

function App() {
  const [health, setHealth] = useState(null);
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("BM-READY-LG-001");
  const [input, setInput] = useState(BENCHMARK_PROMPT);
  const [offline, setOffline] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      kind: "intro",
      content:
        "Describe a maintenance issue in plain language or choose a benchmark scenario. I will clarify missing context, run the workflow, and show the evidence package."
    }
  ]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const bottomRef = useRef(null);

  const isCustomCase = selectedCase === CUSTOM_CASE_ID;

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => response.json())
      .then(setHealth)
      .catch(() => setHealth(null));
    fetch(`${API_URL}/demo/cases`)
      .then((response) => response.json())
      .then((data) => {
        setCases(data.cases || []);
        if (data.cases?.[0]?.case_id) setSelectedCase(data.cases[0].case_id);
      })
      .catch(() => setCases([]));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  const selectedFixture = useMemo(
    () => cases.find((item) => item.case_id === selectedCase),
    [cases, selectedCase]
  );

  function resetConversation(nextCaseId, nextInput) {
    setSelectedCase(nextCaseId);
    setInput(nextInput);
    setSessionId(null);
    setResult(null);
    setError("");
    setMessages([
      {
        role: "assistant",
        kind: "intro",
        content:
          nextCaseId === CUSTOM_CASE_ID
            ? "Describe the issue in plain language. I will ask follow-up questions only when I need missing aircraft or configuration context."
            : "Select a benchmark scenario and send the prepared prompt to run the workflow."
      }
    ]);
  }

  function useScenario(caseId) {
    resetConversation(
      caseId,
      caseId === CUSTOM_CASE_ID
        ? CUSTOM_PROMPT
        : `Analyze ${caseId} and show agent plan, tool calls, evidence gates, citations, and Langfuse trace.`
    );
  }

  async function send({ choiceValue = null, textOverride = null } = {}) {
    const text = choiceValue ? "" : (textOverride ?? input).trim();
    if ((!text && !choiceValue) || busy) return;
    setBusy(true);
    setError("");
    if (choiceValue) {
      setMessages((current) => [...current, { role: "user", kind: "choice", content: choiceValue }]);
    } else {
      setMessages((current) => [...current, { role: "user", kind: "request", content: text }]);
    }
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: choiceValue ? "" : text,
          case_id: isCustomCase ? null : selectedCase,
          offline,
          include_events: true,
          custom_case: isCustomCase,
          session_id: sessionId,
          choice_value: choiceValue
        })
      });
      if (!response.ok) throw new Error(await response.text());
      const data = await response.json();
      setSessionId(data.session_id || null);
      if (!data.needs_clarification) {
        setResult(data);
      }
      const replyMessages = data.needs_clarification
        ? data.messages || []
        : [
            ...(data.answer ? [{ role: "assistant", kind: "answer", content: data.answer }] : []),
            ...((data.messages || []).filter((item) => item.kind !== "status" || !data.answer))
          ];
      setMessages((current) => [...current, ...replyMessages]);
      if (!choiceValue) setInput("");
    } catch (chatError) {
      setError(String(chatError.message || chatError));
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          kind: "error",
          content: "The workflow could not complete. Check API, model endpoint, or use offline fallback."
        }
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="chat-shell">
      <aside className="scenario-rail">
        <div className="brand-block">
          <p className="eyebrow">AABW tracing demo</p>
          <h1>Maintenance Copilot Chat</h1>
          <p>Interactive agent chat with guided follow-up, citations, gates, and hidden trace details.</p>
        </div>
        <div className="mode-card">
          <label className="toggle">
            <input type="checkbox" checked={offline} onChange={(event) => setOffline(event.target.checked)} />
            <span>Offline fallback</span>
          </label>
          <p>{offline ? "No model calls. Deterministic backup demo." : "Online run. Deep Agents and Langfuse tracing enabled by config."}</p>
        </div>
        <div className="scenario-list">
          <h2>Modes</h2>
          <button
            className={isCustomCase ? "selected special" : "special"}
            onClick={() => useScenario(CUSTOM_CASE_ID)}
          >
            <strong>Custom case chat</strong>
            <span>Ask in plain language and answer follow-up choices</span>
          </button>
          <h2>Benchmarks</h2>
          {cases.map((item) => (
            <button
              className={item.case_id === selectedCase ? "selected" : ""}
              key={item.case_id}
              onClick={() => useScenario(item.case_id)}
            >
              <strong>{item.case_id}</strong>
              <span>{item.expected_final_state}</span>
            </button>
          ))}
        </div>
      </aside>

      <section className="chat-panel">
        <div className="chat-header">
          <div>
            <span>{isCustomCase ? "Conversation mode" : "Selected case"}</span>
            <strong>{isCustomCase ? "Custom case chat" : selectedFixture?.case_id || selectedCase}</strong>
          </div>
          <div className={`header-pill ${statusClass(result?.final_state)}`}>
            {result?.final_state || (isCustomCase ? "guided intake" : "waiting")}
          </div>
        </div>

        <div className="chat-stream">
          {messages.map((message, index) => (
            <Message
              message={message}
              key={`${message.role}-${message.kind}-${index}`}
              onChoiceSelect={(value) => send({ choiceValue: value })}
              disabled={busy}
            />
          ))}
          {busy && (
            <article className="message assistant">
              <div className="avatar">
                <Bot size={17} />
              </div>
              <div className="bubble typing">
                <Loader2 size={16} className="spin" />
                <span>Running agent, tools, gates, and trace export...</span>
              </div>
            </article>
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="chat-error">
            <XCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="composer">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                send();
              }
            }}
            placeholder={isCustomCase ? "Describe the issue in plain language..." : "Ask the agent to analyze a defect case..."}
          />
          <button onClick={() => send()} disabled={busy || !input.trim()} title="Send to agent">
            {busy ? <Loader2 size={19} className="spin" /> : <Send size={19} />}
          </button>
        </div>
      </section>

      <aside className="inspector">
        <StatusCard result={result} health={health} />
        <AnswerPanel result={result} />
        <CitationsPanel result={result} />
        <ChecksPanel result={result} />
        <TracePanel result={result} />
        <PromptPanel result={result} />
        <section className="side-card safety">
          <ShieldCheck size={17} />
          <p>Decision support only. Authorized human review is required. Synthetic data is not an approved maintenance source.</p>
        </section>
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
