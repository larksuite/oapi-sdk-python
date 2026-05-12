# Channel SDK: Two-layer Dedup Architecture

This document is an advanced architecture note for applications that need to
customize Channel dedup state. Most bots can use the defaults.

Channel has two dedup layers:

1. **Pipeline layer**: `InboundPipeline` uses a `DedupStore` before full message
   normalization. It catches webhook retries and WebSocket reconnect backfill.
2. **Safety layer**: `SafetyPipeline` uses `SeenCache` before dispatching to
   user handlers. It catches duplicate handler dispatches and can optionally
   consult a shared `ICache`.

The two layers use different protocols because they run at different points in
the pipeline.

## Pipeline Layer: `DedupStore`

`DedupStore` is defined in `lark_oapi.channel.normalize.dedup` and re-exported
from `lark_oapi.channel`.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DedupStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str, ttl_seconds: int) -> None: ...
```

Contract:

- `seen(key)` returns `True` if the key is still considered seen.
- `mark(key, ttl_seconds)` records the key with the TTL supplied by the SDK.
- Implementations should be thread-safe.
- TTL behavior is part of the protocol. Capacity limits and LRU eviction are
  implementation choices, not SDK-enforced protocol methods.

Key helpers:

```python
from lark_oapi.channel import make_event_key, make_message_key

make_event_key("cli_xxx", "evt_xxx")    # "evt:cli_xxx:evt_xxx"
make_message_key("cli_xxx", "om_xxx")   # "msg:cli_xxx:om_xxx"
```

Inject a custom store with `dedup_store=...`:

```python
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    dedup_store=my_dedup_store,
)
```

## Safety Layer: `ICache`

`SeenCache` can use an optional `lark_oapi.core.cache.ICache` implementation.
The current `ICache` interface is synchronous:

```python
class ICache:
    def get(self, key: str) -> str: ...
    def set(self, key: str, value: str, expire: int): ...
```

`expire` is a Unix timestamp in seconds.

The current `ICache` does not expose an atomic `SETNX` primitive. With multiple
workers, shared-cache dedup is best-effort rather than a strict cross-process
coherence boundary. Safe patterns:

- Route events for one app to a single worker.
- Make handlers idempotent on event/message ids.

Inject a shared cache with `safety_cache=...`:

```python
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety_cache=my_cache,
)
```

## Configuration Notes

`DedupConfig.ttl_seconds`, `max_entries`, and `sweep_seconds` are used by the
default in-memory stores. When you pass a custom `dedup_store`, the SDK only
passes `ttl_seconds` into `mark(key, ttl_seconds)`; your store owns any capacity
and eviction behavior.

In this release, `DedupConfig.enabled` controls the pipeline-layer `Deduper`.
The safety layer still runs `SeenCache` dedup.

```python
from lark_oapi.channel import DedupConfig, FeishuChannel, SafetyConfig

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety=SafetyConfig(
        dedup=DedupConfig(
            ttl_seconds=12 * 3600,
            max_entries=5000,
            sweep_seconds=5 * 60,
        ),
    ),
)
```

## Example: JSON File Store

This example persists pipeline-layer dedup state across process restarts. It is
not shipped as an SDK class.

```python
import json
import threading
import time
from collections import OrderedDict
from pathlib import Path

class JsonFileDedupStore:
    def __init__(self, path: Path, *, max_entries: int = 5000) -> None:
        self._path = Path(path)
        self._max = max_entries
        self._lock = threading.Lock()
        self._data = OrderedDict()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text())
            now = time.time()
            self._data = OrderedDict(
                (k, exp)
                for k, exp in raw.items()
                if isinstance(exp, (int, float)) and exp > now
            )
        except (json.JSONDecodeError, OSError):
            self._data = OrderedDict()

    def _persist_locked(self) -> None:
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(dict(self._data)))
        tmp.replace(self._path)

    def seen(self, key: str) -> bool:
        with self._lock:
            exp = self._data.get(key)
            if exp is None:
                return False
            if exp <= time.time():
                self._data.pop(key, None)
                return False
            self._data.move_to_end(key)
            return True

    def mark(self, key: str, ttl_seconds: int) -> None:
        with self._lock:
            self._data[key] = time.time() + ttl_seconds
            self._data.move_to_end(key)
            while len(self._data) > self._max:
                self._data.popitem(last=False)
            self._persist_locked()
```

## Example: Redis `ICache`

This example adapts Redis to the safety-layer `ICache` shape. It is
best-effort because the SDK calls `get()` and `set()` separately.

```python
import time

import redis

class RedisICache:
    def __init__(self, client: redis.Redis, *, prefix: str = "feishu:seen:") -> None:
        self._client = client
        self._prefix = prefix

    def get(self, key: str):
        value = self._client.get(self._prefix + key)
        return value.decode() if value else None

    def set(self, key: str, value: str, expire: int):
        ttl = max(1, int(expire - time.time()))
        self._client.set(self._prefix + key, value, ex=ttl)
```

Return to [Channel module](../channel.md).
