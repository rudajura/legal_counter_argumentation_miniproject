import json
from types import SimpleNamespace

from app.openai_client import (
    _extract_json,
    analyze_weaknesses,
    extract_fact_pattern,
    generate_counterarguments,
)
from app.schemas import AnalyzeResponse


class FakeResponses:
    def __init__(self, response_text):
        self.response_text = response_text
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(output_text=self.response_text)


class FakeClient:
    def __init__(self, response_text):
        self.responses = FakeResponses(response_text)


def test_analyze_weaknesses_parses_json_array(monkeypatch):
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    payload = json.dumps(
        [{"weakness": "Late notice of defect", "description": "The defect was reported late."}]
    )
    client = FakeClient(payload)
    result = analyze_weaknesses(client, "fact pattern", "argument")
    assert result == [
        {"weakness": "Late notice of defect", "description": "The defect was reported late."}
    ]
    assert client.responses.last_kwargs["input"][0]["role"] == "system"
    assert client.responses.last_kwargs["reasoning"] == {"effort": "high"}
    assert client.responses.last_kwargs["max_output_tokens"] == 16000


def test_generate_counterarguments_parses_json_object():
    payload = json.dumps(
        {
            "summary": "The argument is moderately strong.",
            "items": [
                {
                    "weakness": "X",
                    "counterargument": "Y",
                    "strength": "medium",
                    "reasoning": "Z",
                }
            ],
        }
    )
    client = FakeClient(payload)
    result = generate_counterarguments(
        client,
        [{"weakness": "X", "description": "..."}],
        "the case facts",
        "the original argument",
    )
    assert result["summary"] == "The argument is moderately strong."
    assert result["items"][0]["strength"] == "medium"

    sent_prompt = client.responses.last_kwargs["input"][1]["content"]
    assert "the case facts" in sent_prompt
    assert "the original argument" in sent_prompt
    assert '"weakness": "X"' in sent_prompt


def test_generate_counterarguments_normalizes_strength_casing():
    payload = json.dumps(
        {
            "summary": "s",
            "items": [
                {
                    "weakness": "X",
                    "counterargument": "Y",
                    "strength": " High ",
                    "reasoning": "Z",
                }
            ],
        }
    )
    client = FakeClient(payload)
    result = generate_counterarguments(client, [], "facts", "argument")
    assert result["items"][0]["strength"] == "high"


def test_generate_counterarguments_raw_output_validates_against_schema():
    raw = """```json
{
  "summary": "Argumentace je středně silná.",
  "items": [
    {
      "weakness": "Pozdní vytknutí vady",
      "counterargument": "Vada byla vytknuta po uplynutí lhůty.",
      "strength": "High",
      "reasoning": "Ustálená judikatura NS k § 2112 OZ."
    }
  ]
}
```"""
    client = FakeClient(raw)
    result = generate_counterarguments(
        client,
        [{"weakness": "Pozdní vytknutí vady", "description": "..."}],
        "Skutkový stav",
        "Argumentace",
    )
    assert result["items"][0]["strength"] == "high"

    validated = AnalyzeResponse(**result)
    assert validated.items[0].strength == "high"
    assert validated.summary == "Argumentace je středně silná."


def test_extract_fact_pattern_returns_stripped_text(monkeypatch):
    monkeypatch.delenv("OPENAI_EXTRACTION_MODEL", raising=False)
    client = FakeClient("  Skutkový stav vytažený z dokumentu.  ")
    result = extract_fact_pattern(client, "raw document text")
    assert result == "Skutkový stav vytažený z dokumentu."
    assert client.responses.last_kwargs["model"] == "gpt-5.4-nano"
    assert "reasoning" not in client.responses.last_kwargs
    assert "raw document text" in client.responses.last_kwargs["input"][1]["content"]


def test_extract_fact_pattern_respects_model_override(monkeypatch):
    monkeypatch.setenv("OPENAI_EXTRACTION_MODEL", "gpt-5.5-nano")
    client = FakeClient("text")
    extract_fact_pattern(client, "doc")
    assert client.responses.last_kwargs["model"] == "gpt-5.5-nano"


def test_extract_json_strips_markdown_fences():
    raw = '```json\n[{"a": 1}]\n```'
    assert _extract_json(raw) == [{"a": 1}]


def test_extract_json_handles_plain_json():
    raw = '{"a": 1}'
    assert _extract_json(raw) == {"a": 1}
