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

import json
import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Protocol, Union, runtime_checkable


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


class JsonFileDedupStore:
    """Thread-safe JSON-file ``DedupStore`` for single-process persistence.

    The store writes on every ``mark()`` so the frozen ``DedupStore`` protocol
    remains sufficient for cross-restart dedup. ``flush()`` is provided for
    callers that want an explicit sync point, but the pipeline never relies on
    it. This implementation is not a multi-process coordination primitive.
    """

    def __init__(
        self,
        path: Union[str, Path],
        *,
        max_entries: int = 5000,
    ) -> None:
        self._path = Path(path)
        self._max = max(1, int(max_entries))
        self._data: "OrderedDict[str, float]" = OrderedDict()
        self._lock = threading.Lock()
        self._data = self._load()

    def seen(self, key: str) -> bool:
        with self._lock:
            exp = self._data.get(key)
            if exp is None:
                return False
            if exp <= time.time():
                self._data.pop(key, None)
                self._persist_locked()
                return False
            self._data.move_to_end(key)
            return True

    def mark(self, key: str, ttl_seconds: int) -> None:
        with self._lock:
            self._data[key] = time.time() + ttl_seconds
            self._data.move_to_end(key)
            self._evict_locked()
            self._persist_locked()

    def flush(self) -> None:
        with self._lock:
            self._persist_locked()

    def size(self) -> int:
        with self._lock:
            return len(self._data)

    def _load(self) -> "OrderedDict[str, float]":
        if not self._path.exists():
            return OrderedDict()
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return OrderedDict()
        if not isinstance(raw, dict) or raw.get("version") != 1:
            return OrderedDict()
        entries = raw.get("entries")
        if not isinstance(entries, dict):
            return OrderedDict()
        now = time.time()
        out: "OrderedDict[str, float]" = OrderedDict()
        for key, exp in entries.items():
            if isinstance(key, str) and isinstance(exp, (int, float)) and exp > now:
                out[key] = float(exp)
        self._evict_data(out, now=now)
        return out

    def _evict_locked(self) -> None:
        self._evict_data(self._data, now=time.time())

    def _evict_data(self, data: "OrderedDict[str, float]", *, now: float) -> None:
        expired = [key for key, exp in data.items() if exp <= now]
        for key in expired:
            data.pop(key, None)
        while len(data) > self._max:
            data.popitem(last=False)

    def _persist_locked(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "entries": dict(self._data),
        }
        tmp = self._path.with_name(f".{self._path.name}.tmp")
        try:
            tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            os.replace(str(tmp), str(self._path))
        finally:
            try:
                if tmp.exists():
                    tmp.unlink()
            except OSError:
                pass


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
