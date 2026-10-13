"""Tests for per-instance event loop isolation and graceful stop.

Verifies that multiple Client instances can run concurrently in separate
threads without interfering with each other (the root cause of the
"Future attached to a different loop" error in multi-bot deployments).
"""
import asyncio
import threading
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from lark_oapi.ws import client as ws_client
from lark_oapi.ws.client import Client


class _FakeConn:
    """Minimal fake WebSocket connection."""

    def __init__(self):
        self._closed = False
        self._recv_event = asyncio.Event()

    async def recv(self):
        await self._recv_event.wait()
        raise Exception("connection closed")

    async def send(self, data):
        pass

    async def close(self):
        self._closed = True
        self._recv_event.set()


def _make_client():
    """Create a Client with no real network."""
    return Client("app_id", "app_secret", auto_reconnect=False)


def _patch_connect(client, fake_conn):
    """Patch _get_conn_url and websockets.connect to avoid network."""
    client._get_conn_url = lambda: "ws://fake/callback?device_id=d1&service_id=1"
    original_connect = client._connect

    async def patched_connect():
        await client._lock.acquire()
        if client._conn is not None:
            client._lock.release()
            return
        try:
            client._conn = fake_conn
            client._conn_url = "ws://fake"
            client._conn_id = "d1"
            client._service_id = "1"
            client._loop.create_task(client._receive_message_loop())
        finally:
            client._lock.release()

    client._connect = patched_connect


class TestPerInstanceLoop:
    """Each Client.start() creates its own event loop."""

    def test_two_clients_have_independent_loops(self):
        """Two clients started in separate threads use different loops."""
        loops_seen = []
        barrier = threading.Barrier(2, timeout=5)

        def run_client(idx):
            client = _make_client()
            conn = _FakeConn()
            _patch_connect(client, conn)

            # Intercept _run to capture the loop then stop
            original_run = client._run

            async def capture_and_stop():
                loops_seen.append(asyncio.get_running_loop())
                barrier.wait()  # sync both threads
                client._stop_event.set()

            client._run = capture_and_stop
            client.start()

        t1 = threading.Thread(target=run_client, args=(1,))
        t2 = threading.Thread(target=run_client, args=(2,))
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)

        assert len(loops_seen) == 2
        assert loops_seen[0] is not loops_seen[1]

    def test_stop_terminates_start(self):
        """Calling stop() from another thread causes start() to return."""
        client = _make_client()
        conn = _FakeConn()
        _patch_connect(client, conn)

        started = threading.Event()

        original_run = client._run

        async def run_with_signal():
            started.set()
            await original_run()

        client._run = run_with_signal

        t = threading.Thread(target=client.start)
        t.start()

        assert started.wait(timeout=3), "start() did not begin"
        time.sleep(0.1)  # let it settle
        client.stop()
        t.join(timeout=3)
        assert not t.is_alive(), "start() did not return after stop()"

    def test_stop_interrupts_reconnect(self):
        """stop() interrupts the reconnect sleep rather than waiting 120s."""
        client = Client("app_id", "app_secret", auto_reconnect=True)

        connect_attempts = []

        async def failing_connect():
            connect_attempts.append(time.monotonic())
            raise Exception("simulated network failure")

        client._connect = failing_connect

        t0 = time.monotonic()

        def run():
            client.start()

        t = threading.Thread(target=run)
        t.start()
        time.sleep(0.5)  # let it start reconnect loop
        client.stop()
        t.join(timeout=5)

        elapsed = time.monotonic() - t0
        # Should stop within a few seconds, not wait the full 120s interval
        assert elapsed < 10, f"Took {elapsed:.1f}s, expected < 10s"


@pytest.mark.asyncio
class TestStartAsync:
    """start_async() reuses the caller's event loop."""

    async def test_uses_running_loop(self):
        """start_async() uses asyncio.get_running_loop(), not a new one."""
        client = _make_client()
        conn = _FakeConn()
        _patch_connect(client, conn)

        current_loop = asyncio.get_running_loop()

        async def stop_after_start():
            await asyncio.sleep(0.1)
            client.stop()

        current_loop.create_task(stop_after_start())
        await client.start_async()

        # After start_async returns, instance loop should be cleaned up
        assert client._loop is None
        assert client._stop_event is None


class TestBackwardCompatibility:
    """Module-level `loop` variable is still updated for old code."""

    def test_module_loop_updated_after_start(self):
        """After start(), ws_client.loop points to the last used loop."""
        client = _make_client()

        async def immediate_stop():
            client._stop_event.set()

        client._run = immediate_stop
        client.start()

        # loop was set during start() but is now closed
        # The important thing is it was set (not None)
        # It will be the closed loop from the last start() call
        assert ws_client.loop is not None
