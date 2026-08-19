import json
import os

from app.prompts import (
    PHASE1_SYSTEM,
    PHASE2_SYSTEM,
    build_phase1_user_prompt,
    build_phase2_user_prompt,
)

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
THINKING_BUDGET = int(os.environ.get("ANTHROPIC_THINKING_BUDGET", "4000"))


def _call_claude(client, system: str, user: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=THINKING_BUDGET + 2000,
        thinking={"type": "enabled", "budget_tokens": THINKING_BUDGET},
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


def generate_counterarguments(client, weaknesses: list[dict]) -> dict:
    raw = _call_claude(client, PHASE2_SYSTEM, build_phase2_user_prompt(weaknesses))
    return _extract_json(raw)
