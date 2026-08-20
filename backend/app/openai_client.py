import json
import os

from tools.counterargument import PHASE2_SYSTEM, build_phase2_user_prompt
from tools.fact_extraction import EXTRACTION_SYSTEM, build_extraction_user_prompt
from tools.weakness_analysis import PHASE1_SYSTEM, build_phase1_user_prompt


def _call_openai(client, system: str, user: str) -> str:
    model = os.environ.get("OPENAI_MODEL", "gpt-5.5")
    effort = os.environ.get("OPENAI_REASONING_EFFORT", "high")
    response = client.responses.create(
        model=model,
        max_output_tokens=16000,
        reasoning={"effort": effort},
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.output_text


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
        client, PHASE1_SYSTEM, build_phase1_user_prompt(fact_pattern, argument)
    )
    return _extract_json(raw)


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
    )
    result = _extract_json(raw)
    for item in result.get("items", []):
        if isinstance(item.get("strength"), str):
            item["strength"] = item["strength"].strip().lower()
    return result
