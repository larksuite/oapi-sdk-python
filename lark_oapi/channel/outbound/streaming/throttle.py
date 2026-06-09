"""Dual-threshold throttle: fire on (ms_elapsed >= min_ms) OR (pending >= chars).

Exposes three methods:

- `note(delta_chars)` — record that new content arrived; may schedule or fire
- `flush_now()` — force-fire immediately
- `dispose()` — cancel pending timers

`on_fire` is the flush callback (sync; caller ensures it enqueues, not blocks).
"""

import asyncio
import time
from typing import Callable, Optional


class Throttle:
    def __init__(
            self,
            *,
            min_ms: int = 100,
            min_chars: int = 50,
            on_fire: Callable[[], None],
    ) -> None:
        self._min_ms = min_ms
        self._min_chars = min_chars
        self._on_fire = on_fire
        self._pending_chars = 0
        self._last_fire_ms = 0
        self._timer: Optional[asyncio.TimerHandle] = None
        self._running = False

    def note(self, delta_chars: int) -> None:
        self._pending_chars += max(0, delta_chars)
        if self._running:
            return  # a fire is already in flight; the current `on_fire` will sweep
        if self._pending_chars >= self._min_chars:
            self._cancel_timer()
            self._do_fire()
            return
        if self._timer is not None:
            return
        now = _now_ms()
        elapsed = now - self._last_fire_ms
        wait_ms = max(0, self._min_ms - elapsed)
        loop = asyncio.get_running_loop()
        self._timer = loop.call_later(wait_ms / 1000.0, self._do_fire)

    def flush_now(self) -> None:
        self._cancel_timer()
        self._do_fire()

    def dispose(self) -> None:
        self._cancel_timer()

    # ---- internals ----------------------------------------------------------
    def _do_fire(self) -> None:
        # Clear timer/state BEFORE the synchronous ``on_fire`` call — if the
        # callback triggers a re-entrant ``note`` (unusual but legal) we want
        # the state consistent for that call, and we don't want
        # ``self._timer`` to still look "pending" during the fire.
        self._timer = None
        self._pending_chars = 0
        self._last_fire_ms = _now_ms()
        self._running = True
        try:
            self._on_fire()
        finally:
            # ``_running`` guards re-entry into ``on_fire`` from a synchronous
            # ``note`` called inside the fire callback; the actual HTTP work
            # runs off in ``UpdateQueue`` so nothing is "in flight" from our
            # perspective once ``on_fire`` returns.
            self._running = False

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            try:
                self._timer.cancel()
            except Exception:  # pragma: no cover
                pass
            self._timer = None


def _now_ms() -> int:
    # ``time.monotonic`` is immune to NTP steps + DST jumps; ``time.time`` is
    # not. For an interval-based throttle, the former is always correct.
    return int(time.monotonic() * 1000)
