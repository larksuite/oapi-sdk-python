"""Tests for ``Client.stop()`` public shutdown method.

These tests use a mock WebSocket connection and verify that ``stop()``:
  1. Sets ``_auto_reconnect=False`` so the receive loop's exception handler
     doesn't re-establish the connection after we close it.
  2. Cancels the ping loop, receive loop, and main ``_select`` tasks so
     ``loop.close()`` doesn't report "Task was destroyed but it is pending!".
  3. Closes the underlying WebSocket via ``_disconnect()``.
  4. Releases the blocking ``start()`` call by cancelling the main task.
  5. Is idempotent — safe to call when already stopped.
"""
import asyncio
import threading
from types import SimpleNamespace

import pytest

from lark_oapi.ws import client as ws_client


class _FakeConn:
    """Minimal WebSocketClientProtocol stub."""

    def __init__(self):
        self.closed = False
        self._closed_event = asyncio.Event()

    async def close(self):
        self.closed = True
        self._closed_event.set()

    async def recv(self):
        # Block forever until close() is called; mimics live WS behavior
        # where recv() raises ConnectionClosed after the conn shuts down.
        await self._closed_event.wait()
        raise ws_client.ConnectionClosedException("closed")


@pytest.mark.asyncio
async def test_stop_disables_auto_reconnect():
    """``stop()`` must flip ``_auto_reconnect`` off so the receive loop's
    ``except`` handler doesn't reconnect after we close the WebSocket."""
    client = ws_client.Client("app_id", "app_secret", auto_reconnect=True)
    assert client._auto_reconnect is True

    await client.stop()

    assert client._auto_reconnect is False


@pytest.mark.asyncio
async def test_stop_closes_websocket(monkeypatch):
    """``stop()`` must call ``_disconnect()`` to close the underlying WS."""
    client = ws_client.Client("app_id", "app_secret")
    fake_conn = _FakeConn()
    client._conn = fake_conn

    await client.stop()

    assert fake_conn.closed is True
    assert client._conn is None


@pytest.mark.asyncio
async def test_stop_cancels_background_tasks():
    """``stop()`` must cancel ping_task, receive_message_task, and main_task
    so ``loop.close()`` doesn't warn about pending tasks."""
    client = ws_client.Client("app_id", "app_secret")

    async def _forever():
        while True:
            await asyncio.sleep(3600)

    # Plant fake tasks pretending start() already populated them.
    client._ping_task = asyncio.create_task(_forever())
    client._receive_message_task = asyncio.create_task(_forever())
    client._main_task = asyncio.create_task(_forever())

    await client.stop()
    # Give cancellation a chance to propagate.
    await asyncio.sleep(0)

    assert client._ping_task.cancelled() or client._ping_task.done()
    assert client._receive_message_task.cancelled() or client._receive_message_task.done()
    assert client._main_task.cancelled() or client._main_task.done()


@pytest.mark.asyncio
async def test_stop_is_idempotent():
    """Calling ``stop()`` twice should not raise — useful for cleanup paths
    that may run multiple times (signal handlers, finally blocks, etc)."""
    client = ws_client.Client("app_id", "app_secret")
    # No conn, no tasks — simulate "never started" state.
    await client.stop()
    await client.stop()   # second call must not raise

    assert client._auto_reconnect is False


@pytest.mark.asyncio
async def test_stop_handles_already_done_tasks():
    """If background tasks already completed (e.g. WS dropped on its own),
    ``stop()`` should skip cancelling them without error."""
    client = ws_client.Client("app_id", "app_secret")

    async def _quick():
        return

    client._ping_task = asyncio.create_task(_quick())
    client._main_task = asyncio.create_task(_quick())
    # Let them finish.
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert client._ping_task.done()
    assert client._main_task.done()

    # Should not raise even though tasks are already done.
    await client.stop()


def test_stop_from_another_thread():
    """Real-world use case: ``start()`` runs on a worker thread (it blocks
    forever), so ``stop()`` must be called via ``run_coroutine_threadsafe``
    from another thread. Verify the cross-thread pattern works.
    """
    # Loop A: where the SDK "runs" (where stop() will be scheduled to)
    sdk_loop = asyncio.new_event_loop()
    ready = threading.Event()

    def _run_sdk_loop():
        asyncio.set_event_loop(sdk_loop)
        ready.set()
        sdk_loop.run_forever()

    sdk_thread = threading.Thread(target=_run_sdk_loop, daemon=True)
    sdk_thread.start()
    ready.wait(timeout=2)

    try:
        # Build client + plant a fake "blocking main task" on the sdk loop
        # to simulate start() being parked on _select().
        client = ws_client.Client("app_id", "app_secret")

        async def _build_main_task():
            async def _block():
                while True:
                    await asyncio.sleep(3600)
            client._main_task = asyncio.create_task(_block())
            return client._main_task

        main_task_future = asyncio.run_coroutine_threadsafe(_build_main_task(), sdk_loop)
        main_task_future.result(timeout=2)

        # Now call stop() from the test thread, scheduled onto sdk_loop.
        stop_future = asyncio.run_coroutine_threadsafe(client.stop(), sdk_loop)
        stop_future.result(timeout=2)

        # The blocking main task should be cancelled.
        async def _check():
            return client._main_task.cancelled() or client._main_task.done()

        check_future = asyncio.run_coroutine_threadsafe(_check(), sdk_loop)
        assert check_future.result(timeout=2) is True
    finally:
        sdk_loop.call_soon_threadsafe(sdk_loop.stop)
        sdk_thread.join(timeout=2)
