# Channel SDK: Two-Layer Dedup Architecture

This document describes the de-duplication layers in `lark_oapi.channel`,
the protocols you implement to extend them, and three reference
implementations (JSON file, SQLite, Redis best-effort).

## Why two layers?

The Channel SDK runs every inbound event through two independent dedup
checks:

1. **Pipeline layer** — `InboundPipeline` checks the event/message ID against
   a `DedupStore` at the very top of the funnel. This catches:
   - **Webhook retries** — the same event may be POSTed several times if our
     200 response is delayed.
   - **WS reconnect backfill** — after a reconnect, Feishu replays a window
     of recent events; the event ID changes but the message ID does not.

2. **Safety layer** — `SafetyPipeline.push_*` then checks the message/event
   ID against a `SeenCache`. This catches:
   - **Race conditions inside a single process** when two coroutines reach
     `push_message` for the same ID at the same instant.
   - **(Best-effort) cross-process duplicates** when the optional
     `ICache` is Redis-backed.

The layers exist because they have different purposes (transport-level dedup
vs handler-level dedup), different lifetimes (pipeline runs before parsing,
safety runs after), and different concurrency requirements (pipeline is
single-process, safety wants to be cross-process).

## DedupStore (pipeline layer)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DedupStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str, ttl_seconds: int) -> None: ...
```

Contract:

- **`seen(key) -> bool`** — return True if `mark(key, ...)` was called within
  the most recent `ttl_seconds` window, False otherwise.
- **`mark(key, ttl_seconds)`** — record `key` as seen, expiring after
  `ttl_seconds` seconds. The store is responsible for honoring TTL — the SDK
  never calls `evict()` or similar.
- **Threading** — `seen` and `mark` are called from the SDK's background
  loop and may be invoked from multiple threads in tests. Implementations
  must be thread-safe.
- **Capacity** — when the store reaches its configured `max_entries`, it
  must LRU-evict.
- **Frozen** — these method names and signatures will not change in the
  SDK 1.x line.

The two key shapes are produced by the SDK helpers:

```python
from lark_oapi.channel import make_event_key, make_message_key

make_event_key("acc1", "evt1")    # "evt:acc1:evt1"
make_message_key("acc1", "msg1")  # "msg:acc1:msg1"
```

## ICache (safety layer)

```python
# lark_oapi/core/cache.py — synchronous, no SETNX yet
class ICache(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str, expire_at: int) -> None: ...
```

The current `ICache` does **not** expose an atomic SETNX primitive, so
cross-process dedup is best-effort, not a coherence boundary. Two patterns
are safe today:

1. **Single worker per app_id** — route all events for one Feishu app to
   one process (sticky routing or leader election). The default and
   only configuration covered by tests.
2. **Idempotent handlers** — if you must run multiple workers, design your
   `on("message")` handlers to be idempotent on the event id.

A future SDK version may add `ICache.set_if_not_exists`; until then, treat
the cache layer as a best-effort speedup.

## Reference implementation: JSON file (single-process persistence)

Suitable for single-process bots that want dedup state to survive restarts.

```python
import json
import threading
import time
from collections import OrderedDict
from pathlib import Path

class JsonFileDedupStore:
    """Persistent DedupStore backed by a JSON file. Thread-safe, LRU."""

    def __init__(self, path: Path, *, max_entries: int = 5000) -> None:
        self._path = Path(path)
        self._max = max_entries
        self._lock = threading.Lock()
        self._data: "OrderedDict[str, float]" = OrderedDict()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text())
            now = time.time()
            self._data = OrderedDict(
                (k, exp) for k, exp in raw.items() if isinstance(exp, (int, float)) and exp > now
            )
        except (json.JSONDecodeError, OSError):
            # Corrupt / unreadable file — start clean rather than crashing.
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

Inject into the channel:

```python
from pathlib import Path
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    dedup_store=JsonFileDedupStore(
        path=Path.home() / ".myapp/feishu_seen.json",
        max_entries=2048,
    ),
)
```

## Reference implementation: SQLite (single-process persistence, larger working set)

For applications where the JSON-file overhead becomes a bottleneck.

```python
import sqlite3
import threading
import time
from pathlib import Path

class SqliteDedupStore:
    def __init__(self, path: Path, *, max_entries: int = 50_000) -> None:
        self._lock = threading.Lock()
        self._max = max_entries
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            "  key TEXT PRIMARY KEY, expires_at REAL NOT NULL"
            ")"
        )
        self._conn.commit()

    def seen(self, key: str) -> bool:
        with self._lock:
            row = self._conn.execute(
                "SELECT expires_at FROM seen WHERE key = ?", (key,)
            ).fetchone()
            if row is None:
                return False
            if row[0] <= time.time():
                self._conn.execute("DELETE FROM seen WHERE key = ?", (key,))
                self._conn.commit()
                return False
            return True

    def mark(self, key: str, ttl_seconds: int) -> None:
        expire_at = time.time() + ttl_seconds
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO seen(key, expires_at) VALUES (?, ?)",
                (key, expire_at),
            )
            # Trim to max_entries by oldest expiry.
            self._conn.execute(
                "DELETE FROM seen WHERE key NOT IN ("
                "  SELECT key FROM seen ORDER BY expires_at DESC LIMIT ?"
                ")",
                (self._max,),
            )
            self._conn.commit()
```

## Reference implementation: Redis (cross-process best-effort)

`SeenCache` itself is `ICache`-shaped; for cross-process you write a Redis
adapter for `ICache`, NOT for `DedupStore`. Note this is best-effort until
SETNX support lands.

```python
import time
import redis  # not a SDK dependency — bring your own

class RedisICache:
    """ICache adapter over Redis. Best-effort — no atomic SETNX yet."""

    def __init__(self, client: redis.Redis, *, prefix: str = "feishu:seen:") -> None:
        self._client = client
        self._prefix = prefix

    def get(self, key: str):
        v = self._client.get(self._prefix + key)
        return v.decode() if v else None

    def set(self, key: str, value: str, expire_at: int) -> None:
        ttl = max(1, int(expire_at - time.time()))
        self._client.set(self._prefix + key, value, ex=ttl)
```

Inject:

```python
import redis
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety_cache=RedisICache(redis.Redis.from_url("redis://localhost:6379/0")),
)
```

## TTL and capacity

Both layers honor the `DedupConfig` you pass via `safety=SafetyConfig(dedup=...)`:

```python
from lark_oapi.channel import DedupConfig, SafetyConfig

DedupConfig(
    enabled=True,
    ttl_seconds=12 * 3600,    # 12 hours
    max_entries=5000,
    sweep_seconds=5 * 60,     # background sweep period for expired keys
)
```

The pipeline layer reads `ttl_seconds` and passes it to your `DedupStore.mark(key, ttl_seconds)`; the safety layer uses the same config to bound its in-memory `SeenCache`.
