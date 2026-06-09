"""Identity resolution with a bounded LRU + TTL name cache.

Channel handlers often need to turn an open_id into a display name (for
mentions, merge_forward summaries, etc.). This module:

- Caches resolved (open_id → name) entries with a TTL.
- Batches lookups via `resolve_names(open_ids)`.
- Is transport-agnostic: a `ContactLookupFn` is injected.
"""

import inspect
import threading
import time
from collections import OrderedDict
from typing import Awaitable, Callable, Dict, Iterable, List, Optional, Union

from lark_oapi.core.log import logger

from .config import NameCacheConfig
from .types import Identity

ContactLookupResult = Dict[str, Union[Identity, str]]
ContactLookupFn = Callable[
    [List[str]], Union[ContactLookupResult, Awaitable[ContactLookupResult]]
]
"""Signature: given a list of open_ids, return dict[open_id, Identity | str].

Either sync or awaitable return is accepted.
"""


class NameCache:
    """Thread-safe bounded LRU + TTL cache of open_id → display_name."""

    def __init__(self, config: Optional[NameCacheConfig] = None) -> None:
        config = config or NameCacheConfig()
        self._enabled = config.enabled
        self._max = config.max_size
        self._ttl = config.ttl_seconds
        self._data: "OrderedDict[str, tuple[str, float]]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, open_id: str) -> Optional[str]:
        if not self._enabled or not open_id:
            return None
        with self._lock:
            entry = self._data.get(open_id)
            if entry is None:
                return None
            name, exp = entry
            if exp <= time.time():
                self._data.pop(open_id, None)
                return None
            self._data.move_to_end(open_id)
            return name

    def put(self, open_id: str, name: str) -> None:
        if not self._enabled or not open_id or not name:
            return
        with self._lock:
            self._data[open_id] = (name, time.time() + self._ttl)
            self._data.move_to_end(open_id)
            while len(self._data) > self._max:
                self._data.popitem(last=False)

    def invalidate(self, open_id: str) -> None:
        with self._lock:
            self._data.pop(open_id, None)


class IdentityResolver:
    """Async-friendly name resolver."""

    def __init__(
            self,
            lookup: Optional[ContactLookupFn],
            cache: Optional[NameCache] = None,
    ) -> None:
        self._lookup = lookup
        self._cache = cache or NameCache()

    @property
    def cache(self) -> NameCache:
        return self._cache

    async def resolve_names(self, open_ids: Iterable[str]) -> Dict[str, str]:
        """Batch resolve. Returns dict[open_id, name]; missing keys indicate
        lookup failure. Populates the cache on success.
        """
        ids = [o for o in open_ids if o]
        if not ids:
            return {}

        out: Dict[str, str] = {}
        missing: List[str] = []
        for oid in ids:
            cached = self._cache.get(oid)
            if cached:
                out[oid] = cached
            else:
                missing.append(oid)

        if missing and self._lookup is not None:
            try:
                result = self._lookup(missing)
                if inspect.isawaitable(result):
                    result = await result
                if isinstance(result, dict):
                    for oid, ident in result.items():
                        if isinstance(ident, Identity) and ident.display_name:
                            self._cache.put(oid, ident.display_name)
                            out[oid] = ident.display_name
                        elif isinstance(ident, str) and ident:
                            self._cache.put(oid, ident)
                            out[oid] = ident
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("identity: lookup failed for %s ids: %s", len(missing), e)

        return out

    async def resolve(self, open_id: str) -> Identity:
        if not open_id:
            return Identity(open_id="")
        names = await self.resolve_names([open_id])
        return Identity(open_id=open_id, display_name=names.get(open_id))
