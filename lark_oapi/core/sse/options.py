"""Per-call streaming options; ordinary HTTP configuration is unchanged."""

import math
import threading
from dataclasses import dataclass
from typing import Optional


class SSECancellation:
    """A thread-safe cancellation handle, including while a read is blocked."""

    def __init__(self):
        self._lock = threading.Lock()
        self._cancelled = False
        self._callback = None

    def cancel(self):
        with self._lock:
            self._cancelled = True
            callback = self._callback
        if callback is not None:
            callback()

    def bind(self, callback):
        with self._lock:
            self._callback = callback
            cancelled = self._cancelled
        if cancelled and callback is not None:
            callback()

    @property
    def cancelled(self):
        with self._lock:
            return self._cancelled


@dataclass
class SSEOptions:
    open_timeout: float = 10.0
    idle_read_timeout: float = 60.0
    total_timeout: Optional[float] = None
    max_event_bytes: int = 1024 * 1024
    last_event_id: str = ""
    cancellation: Optional[SSECancellation] = None

    def validate(self):
        for name in ("open_timeout", "idle_read_timeout", "total_timeout"):
            value = getattr(self, name)
            if name == "total_timeout" and value is None:
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"SSE {name} must be a positive finite duration")
        if type(self.max_event_bytes) is not int or self.max_event_bytes <= 0:
            raise ValueError("SSE max_event_bytes must be a positive integer")
        if (
            not isinstance(self.last_event_id, str)
            or any(c in self.last_event_id for c in "\r\n\0")
            or len(self.last_event_id.encode()) > 8192
        ):
            raise ValueError("invalid SSE last_event_id")
        if self.cancellation is not None and not isinstance(
            self.cancellation, SSECancellation
        ):
            raise ValueError("invalid SSE cancellation handle")
