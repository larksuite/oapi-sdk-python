"""Two-tier dedup cache: in-memory LRU + optional shared Cache.

- **Memory layer** (default): bounded LRU + TTL, no external dependencies, no
  cross-process coherence.
- **Cache layer** (optional): pluggable `lark_oapi.core.cache.ICache` — usually
  Redis-backed. Lets multiple agent workers share dedup state, and survives
  restarts.

`has(id)` reads memory first; on miss it consults the Cache layer and
back-fills memory if the Cache layer has a hit. `add(id)` writes both.

**Concurrency caveat — single-process dedup is not atomic across workers.**
``has`` + ``add`` is a check-then-act sequence; two concurrent callers for
the same event id may both observe "not seen" and both proceed to the
handler. The in-process :class:`~.processing_lock.ProcessingLock` breaks
the tie within a single process, but does **not** cross process boundaries.

If you run multiple agent workers behind a shared ``ICache`` (e.g. Redis),
the current ``ICache`` interface does not expose an atomic SETNX primitive,
so cross-process duplicate delivery is possible for a short window. The
safe patterns are:

1. **Single worker per app_id.** Route all events for one Feishu app to a
   single process (sticky routing / leader election). This is the default
   assumption and the only configuration fully covered by the tests.
2. **Idempotent handlers.** If you must run multiple workers, design your
   event handlers to be idempotent on the event id.

A future version may add ``ICache.set_if_not_exists`` so the cache layer
itself can serialize concurrent first-writers; until then, treat the cache
layer as a best-effort speedup, not a coherence boundary.
"""

import threading
import time
from collections import OrderedDict
from typing import Optional

from lark_oapi.core.cache import ICache
from lark_oapi.core.log import logger

DEFAULT_TTL_SECONDS = 12 * 3600
DEFAULT_MAX_ENTRIES = 5000
DEFAULT_SWEEP_SECONDS = 5 * 60
DEFAULT_NAMESPACE = "channel:seen:"


class SeenCache:
    """Thread-safe two-layer dedup cache.

    Use `has_sync` / `add_sync` for purely in-memory use; the async variants
    also consult / write the injected `ICache`. Both APIs coexist because the
    underlying `ICache` is synchronous, but we may later plug in an async
    Redis client — the async signatures keep that upgrade path open without
    breaking callers.
    """

    def __init__(
            self,
            cache: Optional[ICache] = None,
            *,
            ttl_seconds: int = DEFAULT_TTL_SECONDS,
            max_entries: int = DEFAULT_MAX_ENTRIES,
            sweep_seconds: int = DEFAULT_SWEEP_SECONDS,
            namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        self._cache = cache
        self._ttl = ttl_seconds
        self._max = max_entries
        self._sweep = sweep_seconds
        self._ns = namespace

        self._memory: "OrderedDict[str, float]" = OrderedDict()
        self._lock = threading.Lock()
        self._last_sweep = time.time()

    # ---- sync API ------------------------------------------------------------
    def has_sync(self, id_: str) -> bool:
        with self._lock:
            self._maybe_sweep_locked()
            exp = self._memory.get(id_)
            if exp is not None:
                if exp > time.time():
                    self._memory.move_to_end(id_)
                    return True
                self._memory.pop(id_, None)
        # Memory miss: check the external cache.
        if self._cache is not None:
            hit = self._cache_get(self._key(id_))
            if hit:
                # Back-fill memory.
                with self._lock:
                    self._memory[id_] = time.time() + self._ttl
                    self._memory.move_to_end(id_)
                    self._evict_locked()
                return True
        return False

    def add_sync(self, id_: str) -> None:
        expire_at = time.time() + self._ttl
        with self._lock:
            self._memory[id_] = expire_at
            self._memory.move_to_end(id_)
            self._evict_locked()
        if self._cache is not None:
            try:
                self._cache.set(self._key(id_), "1", int(expire_at))
            except Exception as e:  # pragma: no cover - defensive
                logger.debug("seen_cache: ICache.set failed: %s", e)

    # ---- async wrappers (identical semantics) --------------------------------
    async def has(self, id_: str) -> bool:
        return self.has_sync(id_)

    async def add(self, id_: str) -> None:
        self.add_sync(id_)

    # ---- internals -----------------------------------------------------------
    def _key(self, id_: str) -> str:
        return f"{self._ns}{id_}"

    def _cache_get(self, key: str) -> Optional[str]:
        try:
            return self._cache.get(key)  # type: ignore[union-attr]
        except Exception as e:
            logger.debug("seen_cache: ICache.get failed: %s", e)
            return None

    def _evict_locked(self) -> None:
        while len(self._memory) > self._max:
            self._memory.popitem(last=False)

    def _maybe_sweep_locked(self) -> None:
        now = time.time()
        if now - self._last_sweep < self._sweep:
            return
        self._last_sweep = now
        expired = [k for k, exp in self._memory.items() if exp <= now]
        for k in expired:
            self._memory.pop(k, None)

    def size(self) -> int:
        with self._lock:
            return len(self._memory)
