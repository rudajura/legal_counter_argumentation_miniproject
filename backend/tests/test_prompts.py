from tools.prompts.counterargument import PHASE2_SYSTEM, build_phase2_user_prompt
from tools.prompts.fact_extraction import EXTRACTION_SYSTEM, build_extraction_user_prompt
from tools.prompts.weakness_analysis import PHASE1_SYSTEM, build_phase1_user_prompt


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


def test_phase1_system_requests_json_array():
    assert "JSON pole" in PHASE1_SYSTEM


def test_phase2_system_requests_json_object_with_summary():
    assert "summary" in PHASE2_SYSTEM
    assert "items" in PHASE2_SYSTEM


def test_build_extraction_user_prompt_includes_document_text():
    prompt = build_extraction_user_prompt("the document contents")
    assert "the document contents" in prompt


def test_extraction_system_requests_facts_only():
    assert "skutkov" in EXTRACTION_SYSTEM.lower()
