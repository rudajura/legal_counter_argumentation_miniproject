import asyncio
import json
from types import SimpleNamespace

from app.openai_client import (
    _extract_json,
    analyze_weaknesses,
    analyze_weaknesses_stream,
    extract_fact_pattern,
    generate_counterarguments,
    generate_counterarguments_stream,
)
from app.schemas import AnalyzeResponse
from tools.prompts.counterargument import PHASE2_JSON_SCHEMA
from tools.prompts.weakness_analysis import PHASE1_JSON_SCHEMA


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


class FakeAsyncStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        return self._agen()

    async def _agen(self):
        for chunk in self._chunks:
            yield SimpleNamespace(type="response.output_text.delta", delta=chunk)


class FakeAsyncResponses:
    def __init__(self, chunks):
        self._chunks = chunks
        self.last_kwargs = None

    async def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeAsyncStream(self._chunks)


class FakeAsyncClient:
    def __init__(self, chunks):
        self.responses = FakeAsyncResponses(chunks)


def test_analyze_weaknesses_parses_json_array(monkeypatch):
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    payload = json.dumps(
        {
            "weaknesses": [
                {
                    "weakness": "Late notice of defect",
                    "description": "The defect was reported late.",
                }
            ]
        }
    )
    client = FakeClient(payload)
    result = analyze_weaknesses(client, "fact pattern", "argument")
    assert result == [
        {"weakness": "Late notice of defect", "description": "The defect was reported late."}
    ]
    assert client.responses.last_kwargs["input"][0]["role"] == "system"
    assert client.responses.last_kwargs["reasoning"] == {"effort": "high"}
    assert client.responses.last_kwargs["max_output_tokens"] == 16000
    text_format = client.responses.last_kwargs["text"]["format"]
    assert text_format["type"] == "json_schema"
    assert text_format["strict"] is True
    assert text_format["schema"] == PHASE1_JSON_SCHEMA


def test_analyze_weaknesses_returns_bare_array_if_model_returns_array(monkeypatch):
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    payload = json.dumps(
        [
            {
                "weakness": "Late notice of defect",
                "description": "The defect was reported late.",
            }
        ]
    )
    client = FakeClient(payload)
    result = analyze_weaknesses(client, "fact pattern", "argument")
    assert result == [
        {"weakness": "Late notice of defect", "description": "The defect was reported late."}
    ]


def test_generate_counterarguments_sends_json_schema_format():
    payload = json.dumps({"summary": "s", "items": []})
    client = FakeClient(payload)
    generate_counterarguments(client, [], "facts", "argument")
    text_format = client.responses.last_kwargs["text"]["format"]
    assert text_format["type"] == "json_schema"
    assert text_format["strict"] is True
    assert text_format["schema"] == PHASE2_JSON_SCHEMA


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


def test_analyze_weaknesses_stream_yields_items_then_done(monkeypatch):
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    chunks = [
        '{"weaknesses": [',
        '{"weakness": "A", "description": "B"}',
        ', {"weakness": "C", "description": "D"}',
        "]}",
    ]
    client = FakeAsyncClient(chunks)

    async def run():
        return [
            event
            async for event in analyze_weaknesses_stream(client, "facts", "argument")
        ]

    events = asyncio.run(run())

    assert events[0] == ("item", {"weakness": "A", "description": "B"})
    assert events[1] == ("item", {"weakness": "C", "description": "D"})
    assert events[2] == (
        "done",
        [
            {"weakness": "A", "description": "B"},
            {"weakness": "C", "description": "D"},
        ],
    )
    assert client.responses.last_kwargs["stream"] is True
    assert client.responses.last_kwargs["reasoning"] == {"effort": "high"}
    text_format = client.responses.last_kwargs["text"]["format"]
    assert text_format["schema"] == PHASE1_JSON_SCHEMA


def test_analyze_weaknesses_stream_handles_bare_array_response():
    chunks = ['[{"weakness": "A", "description": "B"}]']
    client = FakeAsyncClient(chunks)

    async def run():
        return [
            event
            async for event in analyze_weaknesses_stream(client, "facts", "argument")
        ]

    events = asyncio.run(run())
    assert events[-1] == ("done", [{"weakness": "A", "description": "B"}])


def test_generate_counterarguments_stream_yields_items_then_done():
    chunks = [
        '{"items": [',
        '{"weakness": "X", "counterargument": "Y", "strength": " High ", '
        '"reasoning": "Z"}',
        '], "summary": "The argument is moderately strong."}',
    ]
    client = FakeAsyncClient(chunks)

    async def run():
        return [
            event
            async for event in generate_counterarguments_stream(
                client, [{"weakness": "X", "description": "..."}], "facts", "argument"
            )
        ]

    events = asyncio.run(run())

    assert events[0] == (
        "item",
        {
            "weakness": "X",
            "counterargument": "Y",
            "strength": " High ",
            "reasoning": "Z",
        },
    )
    assert events[1][0] == "done"
    result = events[1][1]
    assert result["summary"] == "The argument is moderately strong."
    # strength is normalized in the final authoritative result, same as the
    # non-streaming generate_counterarguments.
    assert result["items"][0]["strength"] == "high"

    validated = AnalyzeResponse(**result)
    assert validated.items[0].strength == "high"
