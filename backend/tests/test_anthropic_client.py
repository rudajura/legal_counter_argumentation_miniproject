import json
from types import SimpleNamespace

from app.anthropic_client import (
    _extract_json,
    analyze_weaknesses,
    generate_counterarguments,
)


class FakeMessages:
    def __init__(self, response_text):
        self.response_text = response_text
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=self.response_text)]
        )


class FakeClient:
    def __init__(self, response_text):
        self.messages = FakeMessages(response_text)


def test_analyze_weaknesses_parses_json_array():
    payload = json.dumps(
        [{"weakness": "Late notice of defect", "description": "The defect was reported late."}]
    )
    client = FakeClient(payload)
    result = analyze_weaknesses(client, "fact pattern", "argument")
    assert result == [
        {"weakness": "Late notice of defect", "description": "The defect was reported late."}
    ]
    assert client.messages.last_kwargs["system"] is not None


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
    result = generate_counterarguments(client, [{"weakness": "X", "description": "..."}])
    assert result["summary"] == "The argument is moderately strong."
    assert result["items"][0]["strength"] == "medium"


def test_extract_json_strips_markdown_fences():
    raw = '```json\n[{"a": 1}]\n```'
    assert _extract_json(raw) == [{"a": 1}]


def test_extract_json_handles_plain_json():
    raw = '{"a": 1}'
    assert _extract_json(raw) == {"a": 1}
