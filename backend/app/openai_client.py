import json
import os

from app.streaming_json import IncrementalArrayParser
from tools.prompts.counterargument import (
    PHASE2_JSON_SCHEMA,
    PHASE2_SYSTEM,
    build_phase2_user_prompt,
)
from tools.prompts.fact_extraction import EXTRACTION_SYSTEM, build_extraction_user_prompt
from tools.prompts.weakness_analysis import (
    PHASE1_JSON_SCHEMA,
    PHASE1_SYSTEM,
    build_phase1_user_prompt,
)


def _build_openai_kwargs(
    system: str,
    user: str,
    json_schema: dict | None = None,
    schema_name: str = "response",
) -> dict:
    model = os.environ.get("OPENAI_MODEL", "gpt-5.5")
    effort = os.environ.get("OPENAI_REASONING_EFFORT", "high")
    kwargs = {
        "model": model,
        "max_output_tokens": 16000,
        "reasoning": {"effort": effort},
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_schema is not None:
        kwargs["text"] = {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": json_schema,
                "strict": True,
            }
        }
    return kwargs


def _call_openai(
    client,
    system: str,
    user: str,
    json_schema: dict | None = None,
    schema_name: str = "response",
) -> str:
    kwargs = _build_openai_kwargs(system, user, json_schema, schema_name)
    response = client.responses.create(**kwargs)
    return response.output_text


async def _stream_openai_items(
    client,
    system: str,
    user: str,
    json_schema: dict,
    schema_name: str,
    array_key: str,
):
    """Streams an OpenAI structured-output call, yielding completed array items.

    Yields ("item", dict) for each object in `array_key`'s array as soon as
    it completes, then a final ("done", raw_text) with the full accumulated
    response text once the stream ends.
    """
    kwargs = _build_openai_kwargs(system, user, json_schema, schema_name)
    kwargs["stream"] = True
    stream = await client.responses.create(**kwargs)

    parser = IncrementalArrayParser(array_key)
    buffer = ""
    async for event in stream:
        if getattr(event, "type", None) == "response.output_text.delta":
            delta = event.delta
            buffer += delta
            for item in parser.feed(delta):
                yield ("item", item)
    yield ("done", buffer)


def _call_openai_extraction(client, system: str, user: str) -> str:
    model = os.environ.get("OPENAI_EXTRACTION_MODEL", "gpt-5.4-nano")
    response = client.responses.create(
        model=model,
        max_output_tokens=4000,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.output_text


def _extract_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[len("json"):]
        raw = raw.strip()
    return json.loads(raw)


def analyze_weaknesses(client, fact_pattern: str, argument: str) -> list[dict]:
    raw = _call_openai(
        client,
        PHASE1_SYSTEM,
        build_phase1_user_prompt(fact_pattern, argument),
        json_schema=PHASE1_JSON_SCHEMA,
        schema_name="weakness_list",
    )
    data = _extract_json(raw)
    return data["weaknesses"] if isinstance(data, dict) else data


def extract_fact_pattern(client, document_text: str) -> str:
    raw = _call_openai_extraction(
        client, EXTRACTION_SYSTEM, build_extraction_user_prompt(document_text)
    )
    return raw.strip()


def generate_counterarguments(
    client, weaknesses: list[dict], fact_pattern: str, argument: str
) -> dict:
    raw = _call_openai(
        client,
        PHASE2_SYSTEM,
        build_phase2_user_prompt(weaknesses, fact_pattern, argument),
        json_schema=PHASE2_JSON_SCHEMA,
        schema_name="counterargument_analysis",
    )
    result = _extract_json(raw)
    for item in result.get("items", []):
        if isinstance(item.get("strength"), str):
            item["strength"] = item["strength"].strip().lower()
    return result


async def analyze_weaknesses_stream(client, fact_pattern: str, argument: str):
    async for kind, payload in _stream_openai_items(
        client,
        PHASE1_SYSTEM,
        build_phase1_user_prompt(fact_pattern, argument),
        PHASE1_JSON_SCHEMA,
        "weakness_list",
        "weaknesses",
    ):
        if kind == "item":
            yield ("item", payload)
        else:
            data = _extract_json(payload)
            weaknesses = data["weaknesses"] if isinstance(data, dict) else data
            yield ("done", weaknesses)


async def generate_counterarguments_stream(
    client, weaknesses: list[dict], fact_pattern: str, argument: str
):
    async for kind, payload in _stream_openai_items(
        client,
        PHASE2_SYSTEM,
        build_phase2_user_prompt(weaknesses, fact_pattern, argument),
        PHASE2_JSON_SCHEMA,
        "counterargument_analysis",
        "items",
    ):
        if kind == "item":
            yield ("item", payload)
        else:
            result = _extract_json(payload)
            for item in result.get("items", []):
                if isinstance(item.get("strength"), str):
                    item["strength"] = item["strength"].strip().lower()
            yield ("done", result)
