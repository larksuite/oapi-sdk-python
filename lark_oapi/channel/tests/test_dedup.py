"""Tests for dedup storage + two-key strategy."""

from lark_oapi.channel.normalize.dedup import Deduper, InMemoryDedupStore, make_event_key, make_message_key


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
