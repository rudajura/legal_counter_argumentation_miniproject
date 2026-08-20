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


def test_build_phase1_user_prompt_includes_inputs():
    prompt = build_phase1_user_prompt("case facts", "my legal position")
    assert "case facts" in prompt
    assert "my legal position" in prompt


def test_build_phase2_user_prompt_serializes_weaknesses_as_json():
    weaknesses = [{"weakness": "A", "description": "B"}]
    prompt = build_phase2_user_prompt(weaknesses, "case facts", "my legal position")
    assert '"weakness": "A"' in prompt
    assert '"description": "B"' in prompt


def test_build_phase2_user_prompt_includes_case_context():
    prompt = build_phase2_user_prompt(
        [{"weakness": "A", "description": "B"}], "case facts", "my legal position"
    )
    assert "case facts" in prompt
    assert "my legal position" in prompt


def test_phase1_system_requests_json_object():
    assert "JSON objekt" in PHASE1_SYSTEM
    assert '"weaknesses"' in PHASE1_SYSTEM


def test_phase2_system_requests_json_object_with_summary():
    assert "summary" in PHASE2_SYSTEM
    assert "items" in PHASE2_SYSTEM


def test_build_extraction_user_prompt_includes_document_text():
    prompt = build_extraction_user_prompt("the document contents")
    assert "the document contents" in prompt


def test_extraction_system_requests_facts_only():
    assert "skutkov" in EXTRACTION_SYSTEM.lower()


def test_phase1_json_schema_is_strict_object_wrapping_weaknesses():
    assert PHASE1_JSON_SCHEMA["type"] == "object"
    assert PHASE1_JSON_SCHEMA["additionalProperties"] is False
    assert PHASE1_JSON_SCHEMA["required"] == ["weaknesses"]
    item_schema = PHASE1_JSON_SCHEMA["properties"]["weaknesses"]["items"]
    assert set(item_schema["required"]) == {"weakness", "description"}
    assert item_schema["additionalProperties"] is False


def test_phase2_json_schema_lists_items_before_summary():
    # Structured Outputs generate fields in schema-declared order; items must
    # come first so counterarguments can stream progressively, with the
    # summary (which needs all items) trailing last.
    assert list(PHASE2_JSON_SCHEMA["properties"].keys()) == ["items", "summary"]


def test_phase2_json_schema_is_strict_object_with_summary_and_items():
    assert PHASE2_JSON_SCHEMA["type"] == "object"
    assert PHASE2_JSON_SCHEMA["additionalProperties"] is False
    assert set(PHASE2_JSON_SCHEMA["required"]) == {"summary", "items"}
    item_schema = PHASE2_JSON_SCHEMA["properties"]["items"]["items"]
    assert set(item_schema["required"]) == {
        "weakness",
        "counterargument",
        "strength",
        "reasoning",
    }
    assert item_schema["additionalProperties"] is False
    assert item_schema["properties"]["strength"]["enum"] == ["low", "medium", "high"]
