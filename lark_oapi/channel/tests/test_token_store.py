"""TokenStore tests."""

import os
import tempfile
import warnings

import pytest

from lark_oapi.channel.auth.token_store import FileTokenStore, InMemoryTokenStore
from lark_oapi.channel.types import UAT


@pytest.mark.asyncio
async def test_inmem_roundtrip():
    s = InMemoryTokenStore()
    await s.set("u1", UAT(access_token="t", scopes=["im:message"]))
    got = await s.get("u1")
    assert got is not None and got.access_token == "t" and got.scopes == ["im:message"]
    await s.delete("u1")
    assert await s.get("u1") is None


@pytest.mark.asyncio
async def test_file_store_persists_across_instances():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "toks.json")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s = FileTokenStore(path)
            await s.set("u2", UAT(access_token="abc", scopes=["im:message"]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            s2 = FileTokenStore(path)
        got = await s2.get("u2")
        assert got is not None and got.access_token == "abc"


@pytest.mark.asyncio
async def test_file_store_warns():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "t.json")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            FileTokenStore(path)
            assert any("not for production" in str(x.message).lower() for x in w)
