import pytest
from pydantic import ValidationError
from app.schemas import AnalyzeResponse


def test_analyze_response_accepts_valid_payload():
    payload = {
        "summary": "The argument is moderately strong.",
        "items": [
            {"weakness": "X", "counterargument": "Y", "strength": "high", "reasoning": "Z"}
        ],
    }
    result = AnalyzeResponse(**payload)
    assert result.summary == "The argument is moderately strong."
    assert result.items[0].strength == "high"


def test_analyze_response_rejects_invalid_strength():
    payload = {
        "summary": "text",
        "items": [
            {"weakness": "X", "counterargument": "Y", "strength": "extreme", "reasoning": "Z"}
        ],
    }
    with pytest.raises(ValidationError):
        AnalyzeResponse(**payload)
