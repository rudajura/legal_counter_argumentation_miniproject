import json
import os

from app.prompts import (
    PHASE1_SYSTEM,
    PHASE2_SYSTEM,
    build_phase1_user_prompt,
    build_phase2_user_prompt,
)


def _call_claude(client, system: str, user: str) -> str:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "".join(text_blocks)


def _extract_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[len("json"):]
        raw = raw.strip()
    return json.loads(raw)


def analyze_weaknesses(client, fact_pattern: str, argument: str) -> list[dict]:
    raw = _call_claude(
        client, PHASE1_SYSTEM, build_phase1_user_prompt(fact_pattern, argument)
    )
    return _extract_json(raw)


def generate_counterarguments(
    client, weaknesses: list[dict], fact_pattern: str, argument: str
) -> dict:
    raw = _call_claude(
        client,
        PHASE2_SYSTEM,
        build_phase2_user_prompt(weaknesses, fact_pattern, argument),
    )
    result = _extract_json(raw)
    for item in result.get("items", []):
        if isinstance(item.get("strength"), str):
            item["strength"] = item["strength"].strip().lower()
    return result
