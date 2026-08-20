import json


class IncrementalArrayParser:
    """Extracts complete JSON objects out of a named array as text streams in.

    Feed it text chunks as they arrive from a streaming JSON response; each
    call to `feed` returns the objects belonging to `array_key`'s array that
    became complete since the previous call, in arrival order.
    """

    def __init__(self, array_key: str):
        self._array_key = array_key
        self._buffer = ""
        self._scan_idx = 0
        self._array_start_found = False
        self._depth = 0
        self._in_string = False
        self._escape = False
        self._item_start: int | None = None

    def feed(self, chunk: str) -> list[dict]:
        self._buffer += chunk

        if not self._array_start_found:
            marker = f'"{self._array_key}"'
            marker_idx = self._buffer.find(marker)
            if marker_idx == -1:
                return []
            bracket_idx = self._buffer.find("[", marker_idx + len(marker))
            if bracket_idx == -1:
                return []
            self._array_start_found = True
            self._scan_idx = bracket_idx + 1

        items = []
        i = self._scan_idx
        n = len(self._buffer)
        while i < n:
            c = self._buffer[i]
            if self._in_string:
                if self._escape:
                    self._escape = False
                elif c == "\\":
                    self._escape = True
                elif c == '"':
                    self._in_string = False
            else:
                if c == '"':
                    self._in_string = True
                elif c == "{":
                    if self._depth == 0:
                        self._item_start = i
                    self._depth += 1
                elif c == "}":
                    self._depth -= 1
                    if self._depth == 0 and self._item_start is not None:
                        item_text = self._buffer[self._item_start : i + 1]
                        items.append(json.loads(item_text))
                        self._item_start = None
                elif c == "]" and self._depth == 0:
                    i += 1
                    break
            i += 1
        self._scan_idx = i
        return items
