"""Short-TTL in-memory lock that complements `SeenCache`.

The two pieces of dedup state serve different purposes:

- `SeenCache` = "this id finished processing at some point" — long TTL (12h),
  survives across reconnects, optionally shared via Redis.
- `ProcessingLock` = "this id is being processed RIGHT NOW by this worker" —
  short TTL (5min), memory-only. Needed because `SeenCache.add()` only happens
  AFTER the handler returns, so during a long-running handler a WS reconnect could
  re-deliver the same event and we'd process it twice.

`acquire(id)` returns False when another coroutine still holds the lock.
"""

import threading
import time

DEFAULT_TTL_MS = 5 * 60 * 1000
# How often to walk the internal dict purging expired entries. Cheap in
# absolute terms (a single pass over a dict that is bounded in practice by
# in-flight request concurrency), but bounded so we never do it more than
# once per minute even under heavy traffic.
DEFAULT_SWEEP_INTERVAL_MS = 60 * 1000


class ProcessingLock:
    def __init__(
            self,
            ttl_ms: int = DEFAULT_TTL_MS,
            *,
            sweep_interval_ms: int = DEFAULT_SWEEP_INTERVAL_MS,
    ) -> None:
        self._ttl_ms = ttl_ms
        self._sweep_interval_ms = sweep_interval_ms
        self._locks: "dict[str, float]" = {}
        self._mu = threading.Lock()
        # Start "due for sweep right now" so the first `acquire` call also
        # clears anything left over from a prior instance that shared the
        # dict (there isn't one today, but belt-and-suspenders).
        self._last_sweep_ms = 0

    @staticmethod
    def _now_ms() -> int:
        # Monotonic clock: immune to NTP steps and DST jumps. Wall-clock
        # would let a clock-rewind silently extend held locks past the
        # intended TTL (or expire them early).
        return int(time.monotonic() * 1000)

    def _maybe_sweep_locked(self, now_ms: int) -> None:
        """Drop expired entries if we haven't swept recently. Call with
        ``self._mu`` already held."""
        if now_ms - self._last_sweep_ms < self._sweep_interval_ms:
            return
        expired = [k for k, exp in self._locks.items() if exp <= now_ms]
        for k in expired:
            self._locks.pop(k, None)
        self._last_sweep_ms = now_ms

    def acquire(self, id_: str) -> bool:
        """Return True if lock was acquired, False if already held and fresh."""
        now_ms = self._now_ms()
        with self._mu:
            self._maybe_sweep_locked(now_ms)
            exp = self._locks.get(id_)
            if exp is not None and exp > now_ms:
                return False
            self._locks[id_] = now_ms + self._ttl_ms
            return True

    def release(self, id_: str) -> None:
        with self._mu:
            self._locks.pop(id_, None)

    def size(self) -> int:
        now_ms = self._now_ms()
        with self._mu:
            expired = [k for k, exp in self._locks.items() if exp <= now_ms]
            for k in expired:
                self._locks.pop(k, None)
            self._last_sweep_ms = now_ms
            return len(self._locks)
