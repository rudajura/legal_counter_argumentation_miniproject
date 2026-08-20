from app.sse import format_sse_event


def test_format_sse_event_produces_event_and_data_lines():
    result = format_sse_event("weaknesses", {"a": 1})
    assert result == 'event: weaknesses\ndata: {"a": 1}\n\n'


def test_format_sse_event_preserves_non_ascii_characters():
    result = format_sse_event("result", {"summary": "středně silná"})
    assert "středně silná" in result
    assert result.endswith("\n\n")
