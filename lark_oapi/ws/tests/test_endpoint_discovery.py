import asyncio
import threading
from contextvars import ContextVar
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from lark_oapi.ws import client as ws


@pytest.mark.parametrize("reconnect", [False, True], ids=["initial", "reconnect"])
async def test_discovery_leaves_loop_responsive(monkeypatch, reconnect):
    loop = asyncio.get_running_loop()
    request_started = asyncio.Event()
    release_response = threading.Event()
    context = ContextVar("request_context", default=None)
    context.set("caller")
    calls = []
    client = ws.Client("app", "secret")
    client._reconnect_nonce = 0
    client._reconnect_count = 1

    def post(url, *, headers, json, timeout=None):
        calls.append((context.get(), timeout))
        loop.call_soon_threadsafe(request_started.set)
        assert release_response.wait(3), "event loop did not run during endpoint discovery"
        return SimpleNamespace(status_code=200, content=b'{"code":40001,"msg":"test error"}')

    monkeypatch.setattr(ws.requests, "post", post)
    attempt = asyncio.create_task(client._reconnect() if reconnect else client._connect())
    try:
        await asyncio.wait_for(request_started.wait(), timeout=3)
    finally:
        release_response.set()
    with pytest.raises(ws.ClientException) as exc:
        await attempt
    assert exc.value.code == 40001
    assert calls == [("caller", (10, 30))]
    assert not client._lock.locked()


async def test_cancelled_discovery_discards_late_response(monkeypatch):
    loop = asyncio.get_running_loop()
    request_started = asyncio.Event()
    release_response = threading.Event()
    worker_finished = asyncio.Event()
    client = ws.Client("app", "secret")
    initial_interval = client._ping_interval
    response = SimpleNamespace(status_code=200, content=(
        b'{"code":0,"data":{"URL":"wss://example.test/?device_id=d&service_id=1",'
        b'"ClientConfig":{"PingInterval":9}}}'
    ))
    monkeypatch.setattr(ws.requests, "post", Mock(return_value=response))
    request_endpoint = client._request_endpoint

    def discover():
        loop.call_soon_threadsafe(request_started.set)
        try:
            assert release_response.wait(3)
            return request_endpoint()
        finally:
            loop.call_soon_threadsafe(worker_finished.set)

    monkeypatch.setattr(client, "_request_endpoint", discover)
    connect = AsyncMock()
    monkeypatch.setattr(ws.websockets, "connect", connect)
    attempt = asyncio.create_task(client._connect())
    try:
        await asyncio.wait_for(request_started.wait(), timeout=3)
        attempt.cancel()
        with pytest.raises(asyncio.CancelledError):
            await attempt
        assert not client._lock.locked()
    finally:
        release_response.set()
    await asyncio.wait_for(worker_finished.wait(), timeout=3)
    assert client._ping_interval == initial_interval
    connect.assert_not_awaited()


async def test_connect_when_already_connected_releases_lock():
    client = ws.Client("app", "secret")
    client._conn = object()
    await client._connect()
    assert not client._lock.locked()
