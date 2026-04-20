"""Identity resolver + name cache tests."""

import pytest

from lark_oapi.channel.config import NameCacheConfig
from lark_oapi.channel.identity import IdentityResolver, NameCache
from lark_oapi.channel.types import Identity


def test_name_cache_ttl_and_lru():
    c = NameCache(NameCacheConfig(max_size=2, ttl_seconds=3600))
    c.put("a", "A")
    c.put("b", "B")
    assert c.get("a") == "A"
    c.put("c", "C")
    # "b" should be evicted; "a" was recently touched via get
    assert c.get("b") is None
    assert c.get("c") == "C"


@pytest.mark.asyncio
async def test_resolver_batches_missing():
    calls = []

    def lookup(ids):
        calls.append(list(ids))
        return {i: Identity(open_id=i, display_name=f"name_{i}") for i in ids}

    r = IdentityResolver(lookup=lookup)
    out = await r.resolve_names(["a", "b"])
    assert out == {"a": "name_a", "b": "name_b"}
    # Second call uses cache for both
    out2 = await r.resolve_names(["a", "b"])
    assert out2 == {"a": "name_a", "b": "name_b"}
    assert len(calls) == 1  # no second lookup


@pytest.mark.asyncio
async def test_resolver_tolerates_lookup_error():
    def lookup(ids):
        raise RuntimeError("boom")

    r = IdentityResolver(lookup=lookup)
    out = await r.resolve_names(["a"])
    assert out == {}


@pytest.mark.asyncio
async def test_resolve_single_returns_identity():
    def lookup(ids):
        return {i: Identity(open_id=i, display_name="N") for i in ids}

    r = IdentityResolver(lookup=lookup)
    ident = await r.resolve("a")
    assert ident.open_id == "a" and ident.display_name == "N"
