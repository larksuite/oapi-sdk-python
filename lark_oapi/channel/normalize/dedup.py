"""Pipeline-layer event de-duplication with pluggable storage.

Two-key dedup: ``(account_id, event_id)`` catches Webhook retries;
``(account_id, message_id)`` also catches WS reconnect backfill where the
event ID changes but the message does not.

Two-layer dedup architecture
============================

The Channel SDK dedups at two distinct layers, and consumers MUST understand
which layer they are extending:

+----------------------+------------------+------------------------+--------------------------+
| Layer                | Protocol         | Constructor parameter  | Trigger point            |
+======================+==================+========================+==========================+
| Pipeline ``Deduper`` | ``DedupStore``   | ``dedup_store=`` (ctor)| ``InboundPipeline``      |
|                      | (this module)    |                        | entry — webhook retries  |
|                      |                  |                        | + WS reconnect backfill  |
+----------------------+------------------+------------------------+--------------------------+
| Safety ``SeenCache`` | ``ICache``       | ``safety_cache=``      | ``SafetyPipeline.push_*``|
|                      | (lark_oapi.core) | (ctor)                 | — pre-dispatch dedup     |
+----------------------+------------------+------------------------+--------------------------+

Both default to in-memory implementations when not supplied. They are
**different protocols** with different methods — this is intentional, not
redundancy. See ``docs/channel/dedup-architecture.md`` for the long-form
explainer including reference implementations.

Frozen contract
===============

The ``DedupStore`` Protocol below — method names, signatures, and semantics
— is **frozen** for the SDK 1.x line. Any change is treated as a breaking
release. Custom implementations written today will keep working without
modification.
"""

import threading
import time
from collections import OrderedDict
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class DedupStore(Protocol):
    def seen(self, key: str) -> bool: ...

    def mark(self, key: str, ttl_seconds: int) -> None: ...


class InMemoryDedupStore:
    """Thread-safe bounded TTL cache; LRU eviction on overflow."""

    def __init__(self, max_entries: int = 5000):
        self._max = max_entries
        self._data: "OrderedDict[str, float]" = OrderedDict()
        self._lock = threading.Lock()

    def seen(self, key: str) -> bool:
        with self._lock:
            exp = self._data.get(key)
            if exp is None:
                return False
            if exp <= time.time():
                self._data.pop(key, None)
                return False
            # touch for LRU ordering
            self._data.move_to_end(key)
            return True

    def mark(self, key: str, ttl_seconds: int) -> None:
        with self._lock:
            self._data[key] = time.time() + ttl_seconds
            self._data.move_to_end(key)
            self._evict_locked()

    def _evict_locked(self) -> None:
        now = time.time()
        # Drop expired entries first (cheap when we overflow)
        while self._data and len(self._data) > self._max:
            # Evict oldest by insertion order.
            k, exp = next(iter(self._data.items()))
            self._data.pop(k, None)
        # Periodic expiry sweep (best-effort)
        if len(self._data) % 64 == 0:
            expired = [k for k, exp in self._data.items() if exp <= now]
            for k in expired:
                self._data.pop(k, None)

    def size(self) -> int:
        return len(self._data)


def make_event_key(account_id: str, event_id: str) -> str:
    return f"evt:{account_id}:{event_id}"


def make_message_key(account_id: str, message_id: str) -> str:
    return f"msg:{account_id}:{message_id}"


class Deduper:
    """Wrapper that combines a DedupStore with the two-key strategy."""

    def __init__(self, store: Optional[DedupStore], ttl_seconds: int, enabled: bool = True):
        self._store = store
        self._ttl = ttl_seconds
        self._enabled = enabled and store is not None

    def check_and_mark(self, account_id: str, event_id: Optional[str], message_id: Optional[str]) -> bool:
        """Return True if the event should be processed (not a duplicate)."""
        if not self._enabled or self._store is None:
            return True
        if event_id:
            k1 = make_event_key(account_id, event_id)
            if self._store.seen(k1):
                return False
        if message_id:
            k2 = make_message_key(account_id, message_id)
            if self._store.seen(k2):
                return False
        if event_id:
            self._store.mark(make_event_key(account_id, event_id), self._ttl)
        if message_id:
            self._store.mark(make_message_key(account_id, message_id), self._ttl)
        return True
