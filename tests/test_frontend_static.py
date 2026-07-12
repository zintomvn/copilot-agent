from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_answer_layout_uses_structured_sections() -> None:
    main = (ROOT / "frontend/src/main.jsx").read_text(encoding="utf-8")
    css = (ROOT / "frontend/src/styles.css").read_text(encoding="utf-8")

    assert "function parseAnswerSections" in main
    assert "function AnswerContent" in main
    assert 'message.kind === "answer" ? <AnswerContent answer={message.content} />' in main
    assert "<AnswerContent answer={result.answer} />" in main
    assert "answer-section fix-path" in main
    assert "answer-citation" in main
    assert ".answer-layout" in css
    assert ".answer-section.fix-path" in css
    assert ".answer-citation" in css
