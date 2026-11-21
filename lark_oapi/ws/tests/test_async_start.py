import asyncio

import pytest

from lark_oapi.ws import client as ws_client
from lark_oapi.ws.exception import ClientException


class _FakeConn:
    async def close(self):
        pass

    async def recv(self):
        # Never used directly by these tests; present so the fake looks like a
        # real connection to any code path that pokes at it.
        await asyncio.sleep(3600)


def test_no_module_level_event_loop_global():
    # Importing the client must not create or capture a process-wide loop at
    # import time. A lingering module global is the root cause behind #133.
    assert not hasattr(ws_client, "loop")


async def test_start_async_runs_on_caller_loop(monkeypatch):
    client = ws_client.Client("app_id", "app_secret")
    captured = {}

    async def fake_connect():
        captured["connect_loop"] = asyncio.get_running_loop()
        client._conn = _FakeConn()

    async def fake_select():
        # Stand in for the long-lived idle wait so start_async does not block
        # the test forever.
        return

    async def fake_ping_loop():
        captured["ping_loop"] = asyncio.get_running_loop()

    monkeypatch.setattr(client, "_connect", fake_connect)
    monkeypatch.setattr(ws_client, "_select", fake_select)
    monkeypatch.setattr(client, "_ping_loop", fake_ping_loop)

    caller = asyncio.get_running_loop()
    await client.start_async()
    # Give the scheduled ping task a chance to run on the caller loop.
    await asyncio.sleep(0)

    assert captured["connect_loop"] is caller
    assert captured["ping_loop"] is caller
    assert client._conn is not None


def test_sync_start_delegates_to_start_async(monkeypatch):
    # Synchronous test with NO running loop, modelling a plain worker thread /
    # script (e.g. channel.py's executor worker). start() must build/acquire a
    # loop of its own and run start_async() to completion.
    client = ws_client.Client("app_id", "app_secret")
    ran = {}

    async def fake_start_async():
        ran["called"] = True
        ran["loop"] = asyncio.get_running_loop()

    monkeypatch.setattr(client, "start_async", fake_start_async)

    try:
        client.start()

        assert ran["called"] is True
        assert ran["loop"] is not None
    finally:
        # Avoid leaking a loop into subsequent tests in this process.
        asyncio.set_event_loop(None)


async def test_sync_start_in_running_loop_raises_clear_error():
    # The test body itself runs inside a live loop, modelling a mistaken sync
    # start() call from within an async framework (#96). The error must point
    # the user at start_async(), not the opaque native message.
    client = ws_client.Client("app_id", "app_secret")

    with pytest.raises(RuntimeError) as err:
        client.start()

    assert "start_async" in str(err.value)


async def test_start_async_propagates_client_exception(monkeypatch):
    client = ws_client.Client("app_id", "app_secret")
    rc = {"n": 0}

    async def fake_connect():
        raise ClientException(403, "forbidden")

    async def fake_reconnect():
        rc["n"] += 1

    monkeypatch.setattr(client, "_connect", fake_connect)
    monkeypatch.setattr(client, "_reconnect", fake_reconnect)

    with pytest.raises(ClientException):
        await client.start_async()

    # Credential/auth failures bubble up untouched and never trigger reconnect.
    assert rc["n"] == 0


async def test_start_async_generic_error_triggers_reconnect(monkeypatch):
    client = ws_client.Client("app_id", "app_secret", auto_reconnect=True)
    rc = {"n": 0}

    async def fake_connect():
        raise RuntimeError("net")

    async def fake_disconnect():
        return

    async def fake_reconnect():
        rc["n"] += 1

    async def fake_select():
        return

    async def fake_ping_loop():
        return

    monkeypatch.setattr(client, "_connect", fake_connect)
    monkeypatch.setattr(client, "_disconnect", fake_disconnect)
    monkeypatch.setattr(client, "_reconnect", fake_reconnect)
    monkeypatch.setattr(ws_client, "_select", fake_select)
    monkeypatch.setattr(client, "_ping_loop", fake_ping_loop)

    await client.start_async()

    # A generic (non-ClientException) failure under auto_reconnect must run the
    # disconnect + reconnect path exactly once.
    assert rc["n"] == 1
