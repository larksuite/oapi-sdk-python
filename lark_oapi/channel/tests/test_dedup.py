"""Tests for dedup storage + two-key strategy."""

import json
import inspect
from concurrent.futures import ThreadPoolExecutor
import time

from lark_oapi.channel.normalize.dedup import (
    Deduper,
    DedupStore,
    InMemoryDedupStore,
    JsonFileDedupStore,
    make_event_key,
    make_message_key,
)


def test_basic_mark_and_seen():
    s = InMemoryDedupStore()
    assert s.seen("k") is False
    s.mark("k", ttl_seconds=60)
    assert s.seen("k") is True


def test_ttl_expires():
    s = InMemoryDedupStore()
    s.mark("k", ttl_seconds=0)
    # ttl=0 is effectively expired immediately
    assert s.seen("k") is False


def test_lru_bounded():
    s = InMemoryDedupStore(max_entries=3)
    s.mark("a", 60)
    s.mark("b", 60)
    s.mark("c", 60)
    s.mark("d", 60)
    # 'a' must have been evicted
    assert s.seen("a") is False
    assert s.seen("d") is True


def test_two_key_dedupes_by_event_id_first():
    s = InMemoryDedupStore()
    d = Deduper(s, ttl_seconds=60)
    assert d.check_and_mark("app", "e1", "m1") is True
    assert d.check_and_mark("app", "e1", "m2") is False  # event_id dup


def test_two_key_dedupes_by_message_id():
    s = InMemoryDedupStore()
    d = Deduper(s, ttl_seconds=60)
    assert d.check_and_mark("app", "e1", "m1") is True
    assert d.check_and_mark("app", "e2", "m1") is False  # message_id dup


def test_different_accounts_do_not_collide():
    s = InMemoryDedupStore()
    d = Deduper(s, ttl_seconds=60)
    assert d.check_and_mark("app1", "e1", "m1") is True
    assert d.check_and_mark("app2", "e1", "m1") is True


def test_dedup_disabled_always_passes():
    s = InMemoryDedupStore()
    d = Deduper(s, ttl_seconds=60, enabled=False)
    assert d.check_and_mark("app", "e1", "m1") is True
    assert d.check_and_mark("app", "e1", "m1") is True


def test_key_builders():
    assert make_event_key("a", "e") == "evt:a:e"
    assert make_message_key("a", "m") == "msg:a:m"


def test_json_file_store_mark_persists_immediately(tmp_path):
    path = tmp_path / "dedup.json"
    store = JsonFileDedupStore(path)

    store.mark("msg:app:om_1", ttl_seconds=60)

    reloaded = JsonFileDedupStore(path)
    assert reloaded.seen("msg:app:om_1") is True


def test_json_file_store_implements_protocol_without_requiring_flush(tmp_path):
    store = JsonFileDedupStore(tmp_path / "dedup.json")

    assert isinstance(store, DedupStore)
    assert hasattr(store, "flush")
    assert "flush" not in DedupStore.__dict__


def test_json_file_store_constructor_does_not_expose_unused_flush_options():
    sig = inspect.signature(JsonFileDedupStore)

    assert "flush_idle_seconds" not in sig.parameters
    assert "flush_dirty_threshold" not in sig.parameters


def test_json_file_store_expires_entries(tmp_path):
    store = JsonFileDedupStore(tmp_path / "dedup.json")

    store.mark("expired", ttl_seconds=0)

    assert store.seen("expired") is False


def test_json_file_store_lru_evicts_oldest_entry(tmp_path):
    store = JsonFileDedupStore(tmp_path / "dedup.json", max_entries=2)

    store.mark("a", ttl_seconds=60)
    store.mark("b", ttl_seconds=60)
    assert store.seen("a") is True
    store.mark("c", ttl_seconds=60)

    assert store.seen("b") is False
    assert store.seen("a") is True
    assert store.seen("c") is True


def test_json_file_store_corrupt_json_starts_empty(tmp_path):
    path = tmp_path / "dedup.json"
    path.write_text("{not json", encoding="utf-8")

    store = JsonFileDedupStore(path)

    assert store.seen("anything") is False
    store.mark("fresh", ttl_seconds=60)
    assert JsonFileDedupStore(path).seen("fresh") is True


def test_json_file_store_writes_versioned_format(tmp_path):
    path = tmp_path / "dedup.json"
    store = JsonFileDedupStore(path)

    store.mark("k", ttl_seconds=60)

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["version"] == 1
    assert set(raw["entries"]) == {"k"}


def test_json_file_store_seen_mark_are_thread_safe(tmp_path):
    path = tmp_path / "dedup.json"
    store = JsonFileDedupStore(path, max_entries=100)

    def mark(idx):
        key = f"k{idx}"
        store.mark(key, ttl_seconds=60)
        return store.seen(key)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(mark, range(40)))

    assert all(results)
    reloaded = JsonFileDedupStore(path, max_entries=100)
    assert all(reloaded.seen(f"k{i}") for i in range(40))
