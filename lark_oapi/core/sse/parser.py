"""Incremental SSE framing, independent of HTTP and business payload schemas."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SSEEvent:
    event: str
    data: str
    id: Optional[str] = None


class SSEParser:
    def __init__(self, max_event_bytes: int, last_event_id: str = ""):
        self.limit = max_event_bytes
        self.last_event_id = last_event_id
        self.retry_delay = None
        self._line = bytearray()
        self._size = 0
        self._first = True
        self._skip_lf = False
        self._data = []
        self._event = ""
        self._id = None

    def feed(self, chunk: bytes):
        """Yield at each blank line; retain only a bounded incomplete event."""
        for byte in chunk:
            if self._skip_lf:
                self._skip_lf = False
                if byte == 10:
                    continue
            self._size += 1
            if self._size > self.limit:
                raise ValueError("SSE event exceeds max_event_bytes")
            if byte not in (10, 13):
                self._line.append(byte)
                continue
            self._skip_lf = byte == 13
            line = self._line.decode("utf-8", errors="replace")
            self._line.clear()
            if self._first:
                self._first = False
                line = line[1:] if line.startswith("\ufeff") else line
            event = self._consume(line)
            if event is not None:
                yield event

    def _consume(self, line):
        if not line:
            return self._finish()
        if line.startswith(":"):
            return None
        key, _separator, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if key == "data":
            self._data.append(value)
        elif key == "event":
            self._event = value
        elif key == "id" and "\0" not in value:
            self._id = value
        elif (
            key == "retry"
            and value
            and all("0" <= c <= "9" for c in value)
            and len(value) <= 19
            and int(value) <= 9223372036854775807
        ):
            # Keep diagnostics bounded and consistent with the other SDKs.
            self.retry_delay = int(value)
        return None

    def _finish(self):
        if self._id is not None:
            self.last_event_id = self._id
        event = None
        if self._data:
            event = SSEEvent(self._event or "message", "\n".join(self._data), self._id)
        self._data = []
        self._event = ""
        self._id = None
        self._size = 0
        return event
