import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.fixtures.invalid_termination import (
    ARGUMENT,
    FACT_PATTERN,
    INVALID_TERMINATION_RESPONSES,
)


def test_weaknesses_endpoint_returns_weaknesses_and_fact_pattern(monkeypatch):
    def fake_analyze_weaknesses(client, fact_pattern, argument):
        assert "case facts" in fact_pattern
        return [{"weakness": "Late notice", "description": "weakness description"}]

    monkeypatch.setattr("app.main.analyze_weaknesses", fake_analyze_weaknesses)
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    response = client.post(
        "/api/analyze/weaknesses",
        data={"fact_pattern": "case facts", "argument": "my argument"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_fact_pattern"] == "case facts"
    assert body["weaknesses"][0]["weakness"] == "Late notice"


def test_weaknesses_endpoint_extracts_uploaded_pdf_text(monkeypatch, tmp_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Sample attachment text")
    pdf_path = tmp_path / "attachment.pdf"
    pdf_path.write_bytes(bytes(pdf.output()))

    captured = {}

    def fake_analyze_weaknesses(client, fact_pattern, argument):
        captured["fact_pattern"] = fact_pattern
        return [{"weakness": "W", "description": "D"}]

    monkeypatch.setattr("app.main.analyze_weaknesses", fake_analyze_weaknesses)
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/analyze/weaknesses",
            data={"fact_pattern": "case facts", "argument": "my argument"},
            files={"files": ("attachment.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert "Sample attachment text" in captured["fact_pattern"]
    assert "Sample attachment text" in body["full_fact_pattern"]


def test_extract_fact_pattern_endpoint_returns_extracted_text(monkeypatch, tmp_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Sample attachment text")
    pdf_path = tmp_path / "attachment.pdf"
    pdf_path.write_bytes(bytes(pdf.output()))

    def fake_extract_fact_pattern(client, document_text):
        assert "Sample attachment text" in document_text
        return "Extracted fact pattern"

    monkeypatch.setattr(
        "app.main.extract_fact_pattern", fake_extract_fact_pattern
    )
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/extract/fact-pattern",
            files={"files": ("attachment.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json() == {"fact_pattern": "Extracted fact pattern"}


def test_extract_fact_pattern_endpoint_requires_at_least_one_file():
    client = TestClient(app)
    response = client.post("/api/extract/fact-pattern")
    assert response.status_code == 422


def test_counterarguments_endpoint_returns_structured_result(monkeypatch):
    def fake_generate_counterarguments(client, weaknesses, fact_pattern, argument):
        assert weaknesses[0]["weakness"] == "Late notice"
        assert fact_pattern == "case facts"
        assert argument == "my argument"
        return {
            "summary": "summary text",
            "items": [
                {
                    "weakness": "Late notice",
                    "counterargument": "counterargument text",
                    "strength": "high",
                    "reasoning": "reasoning text",
                }
            ],
        }

    monkeypatch.setattr(
        "app.main.generate_counterarguments", fake_generate_counterarguments
    )
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    response = client.post(
        "/api/analyze/counterarguments",
        json={
            "weaknesses": [
                {"weakness": "Late notice", "description": "weakness description"}
            ],
            "full_fact_pattern": "case facts",
            "argument": "my argument",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "summary text"
    assert body["items"][0]["strength"] == "high"


@pytest.mark.parametrize("fixture_response", INVALID_TERMINATION_RESPONSES)
def test_counterarguments_endpoint_returns_invalid_termination_fixture(
    monkeypatch, fixture_response
):
    def fake_generate_counterarguments(client, weaknesses, fact_pattern, argument):
        assert fact_pattern == FACT_PATTERN
        assert argument == ARGUMENT
        return fixture_response

    monkeypatch.setattr(
        "app.main.generate_counterarguments", fake_generate_counterarguments
    )
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    response = client.post(
        "/api/analyze/counterarguments",
        json={
            "weaknesses": [
                {
                    "weakness": item["weakness"],
                    "description": item["reasoning"],
                }
                for item in fixture_response["items"]
            ],
            "full_fact_pattern": FACT_PATTERN,
            "argument": ARGUMENT,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == fixture_response


def _parse_sse_events(lines: list[str]) -> list[tuple[str, dict]]:
    events = []
    current_event = None
    for line in lines:
        if line.startswith("event: "):
            current_event = line[len("event: "):]
        elif line.startswith("data: "):
            events.append((current_event, json.loads(line[len("data: "):])))
    return events


def test_stream_endpoint_emits_weaknesses_then_result(monkeypatch):
    def fake_analyze_weaknesses(client, fact_pattern, argument):
        assert "case facts" in fact_pattern
        return [{"weakness": "Late notice", "description": "weakness description"}]

    def fake_generate_counterarguments(client, weaknesses, fact_pattern, argument):
        assert weaknesses[0]["weakness"] == "Late notice"
        return {
            "summary": "summary text",
            "items": [
                {
                    "weakness": "Late notice",
                    "counterargument": "counterargument text",
                    "strength": "high",
                    "reasoning": "reasoning text",
                }
            ],
        }

    monkeypatch.setattr("app.main.analyze_weaknesses", fake_analyze_weaknesses)
    monkeypatch.setattr(
        "app.main.generate_counterarguments", fake_generate_counterarguments
    )
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    with client.stream(
        "POST",
        "/api/analyze/stream",
        data={"fact_pattern": "case facts", "argument": "my argument"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        events = _parse_sse_events(list(response.iter_lines()))

    assert events[0][0] == "weaknesses"
    assert events[0][1]["weaknesses"][0]["weakness"] == "Late notice"
    assert events[0][1]["full_fact_pattern"] == "case facts"
    assert events[1][0] == "result"
    assert events[1][1]["summary"] == "summary text"
    assert events[1][1]["items"][0]["strength"] == "high"


def test_stream_endpoint_emits_error_event_when_phase_one_fails(monkeypatch):
    def failing_analyze_weaknesses(client, fact_pattern, argument):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("app.main.analyze_weaknesses", failing_analyze_weaknesses)
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    with client.stream(
        "POST",
        "/api/analyze/stream",
        data={"fact_pattern": "case facts", "argument": "my argument"},
    ) as response:
        assert response.status_code == 200
        events = _parse_sse_events(list(response.iter_lines()))

    assert events == [("error", {"message": "model unavailable", "phase": "weaknesses"})]


def test_stream_endpoint_extracts_uploaded_pdf_text(monkeypatch, tmp_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Sample attachment text")
    pdf_path = tmp_path / "attachment.pdf"
    pdf_path.write_bytes(bytes(pdf.output()))

    captured = {}

    def fake_analyze_weaknesses(client, fact_pattern, argument):
        captured["fact_pattern"] = fact_pattern
        return [{"weakness": "W", "description": "D"}]

    def fake_generate_counterarguments(client, weaknesses, fact_pattern, argument):
        return {"summary": "s", "items": []}

    monkeypatch.setattr("app.main.analyze_weaknesses", fake_analyze_weaknesses)
    monkeypatch.setattr(
        "app.main.generate_counterarguments", fake_generate_counterarguments
    )
    monkeypatch.setattr("app.main.get_client", lambda: object())

    client = TestClient(app)
    with open(pdf_path, "rb") as f:
        with client.stream(
            "POST",
            "/api/analyze/stream",
            data={"fact_pattern": "case facts", "argument": "my argument"},
            files={"files": ("attachment.pdf", f, "application/pdf")},
        ) as response:
            list(response.iter_lines())

    assert "Sample attachment text" in captured["fact_pattern"]
