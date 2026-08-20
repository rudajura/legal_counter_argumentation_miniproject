from app.streaming_json import IncrementalArrayParser


def test_returns_empty_before_array_key_appears():
    parser = IncrementalArrayParser("weaknesses")
    assert parser.feed('{"weak') == []


def test_parses_single_complete_item_in_one_chunk():
    parser = IncrementalArrayParser("weaknesses")
    items = parser.feed('{"weaknesses": [{"weakness": "A", "description": "B"}]}')
    assert items == [{"weakness": "A", "description": "B"}]


def test_parses_item_split_across_multiple_chunks():
    parser = IncrementalArrayParser("weaknesses")
    text = '{"weaknesses": [{"weakness": "A", "description": "B"}]}'
    collected = []
    for i in range(0, len(text), 7):
        collected.extend(parser.feed(text[i : i + 7]))
    assert collected == [{"weakness": "A", "description": "B"}]


def test_yields_each_item_as_soon_as_it_completes():
    parser = IncrementalArrayParser("weaknesses")
    first = parser.feed('{"weaknesses": [{"weakness": "A", "description": "B"')
    assert first == []
    second = parser.feed("}")
    assert second == [{"weakness": "A", "description": "B"}]
    third = parser.feed(', {"weakness": "C", "description": "D"}')
    assert third == [{"weakness": "C", "description": "D"}]
    fourth = parser.feed("]}")
    assert fourth == []


def test_ignores_braces_inside_string_values():
    parser = IncrementalArrayParser("weaknesses")
    items = parser.feed(
        '{"weaknesses": [{"weakness": "A", "description": "viz {note}"}]}'
    )
    assert items == [{"weakness": "A", "description": "viz {note}"}]


def test_ignores_escaped_quotes_inside_string_values():
    parser = IncrementalArrayParser("weaknesses")
    items = parser.feed(
        '{"weaknesses": [{"weakness": "A", "description": "je \\"citace\\""}]}'
    )
    assert items[0]["description"] == 'je "citace"'


def test_preserves_czech_diacritics():
    parser = IncrementalArrayParser("weaknesses")
    items = parser.feed(
        '{"weaknesses": [{"weakness": "Neplatná výpověď", "description": "středně silná"}]}'
    )
    assert items == [
        {"weakness": "Neplatná výpověď", "description": "středně silná"}
    ]


def test_supports_arbitrary_array_key():
    parser = IncrementalArrayParser("items")
    items = parser.feed(
        '{"summary": "s", "items": [{"weakness": "A", "counterargument": "B", '
        '"strength": "high", "reasoning": "C"}]}'
    )
    assert items == [
        {
            "weakness": "A",
            "counterargument": "B",
            "strength": "high",
            "reasoning": "C",
        }
    ]


def test_does_not_trigger_on_a_different_key_containing_the_same_substring():
    parser = IncrementalArrayParser("items")
    assert parser.feed('{"weaknesses": [{"weakness": "A"}]') == []
