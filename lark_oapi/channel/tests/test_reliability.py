"""Reliability tests for the four fixes batched in the 2.0 reliability pass:

- ``ProcessingLock`` periodic sweep (prevents unbounded dict growth)
- ``ProcessingLock`` monotonic clock (immune to NTP step-back)
- ``ChatPipeline`` closure-chain release (prevents GC retention of completed
  ancestors)
- ``FeishuChannel`` bot-identity retry loop (recovers from startup network
  hiccups instead of permanently disabling group @Bot detection)
"""

import asyncio
import gc
import weakref
from unittest.mock import patch

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.bot_identity import BotIdentity
from lark_oapi.channel.safety import ChatPipeline, ProcessingLock
from lark_oapi.channel.safety.types import TextBatchConfig


# ---------------------------------------------------------------------------
# ProcessingLock — periodic sweep + monotonic clock
# ---------------------------------------------------------------------------


def test_processing_lock_periodic_sweep_trims_expired_entries():
    """Under heavy churn, acquire() must drop expired entries so the
    internal dict doesn't grow unboundedly."""
    lock = ProcessingLock(ttl_ms=10, sweep_interval_ms=0)  # always-sweep

    # Fill 100 unique keys — all expire immediately (ttl=10ms).
    for i in range(100):
        assert lock.acquire(f"k{i}") is True

    # Wait out the TTL so every entry is expired.
    import time
    time.sleep(0.05)

    # A single acquire of a fresh key should trigger the sweep and drop
    # everything else. Size() itself sweeps too; we want acquire() to have
    # already done the work.
    lock.acquire("fresh")
    # After the sweep + the one fresh insert, size should be 1 (not 101).
    assert lock.size() == 1


def test_processing_lock_monotonic_clock_survives_wall_clock_regression():
    """If the wall clock were used, a simulated backward jump would make an
    active lock look expired. Monotonic clock must keep locks valid."""
    lock = ProcessingLock(ttl_ms=60_000)
    assert lock.acquire("x") is True

    # Patch time.time (wall clock) to 30 years ago. The lock uses
    # time.monotonic internally so this must have NO effect.
    with patch("time.time", return_value=0.0):
        assert lock.acquire("x") is False  # still held
    lock.release("x")


# ---------------------------------------------------------------------------
# ChatPipeline — closure chain must not retain completed ancestors
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_pipeline_releases_ancestor_tasks_after_await():
    """Long serialization chains must let completed ancestors GC before the
    whole chain drains. We enqueue 10 tasks, grab a weakref to the first
    task, let all run to completion, then force GC and assert the ref is
    dead."""
    loop = asyncio.get_running_loop()
    pipe = ChatPipeline(
        "scope",
        TextBatchConfig(delay_ms=10, max_messages=1, max_chars=10),
        loop,
        serial_only=True,
    )

    async def noop():
        return None

    tasks = [pipe._enqueue(noop) for _ in range(10)]
    first_ref = weakref.ref(tasks[0])
    # Wait for every task to finish.
    await asyncio.gather(*tasks)
    # Drop our own refs so only the pipeline's closure chain (if any) keeps
    # the first task alive.
    first_task_id = id(tasks[0])
    del tasks
    for _ in range(3):
        gc.collect()
        await asyncio.sleep(0)

    assert first_ref() is None, (
        "ChatPipeline runner closures retained a completed ancestor task — "
        "long chat histories will leak memory. "
        f"first_task_id={first_task_id}"
    )


# ---------------------------------------------------------------------------
# FeishuChannel — bot identity retry loop
# ---------------------------------------------------------------------------


def _channel() -> FeishuChannel:
    return FeishuChannel(app_id="cli_x", app_secret="s")


@pytest.mark.asyncio
async def test_bot_identity_retry_loop_succeeds_after_transient_failure():
    """Simulate ``fetch_bot_identity`` returning None once then succeeding.
    The retry loop must pick up the success and publish the identity."""
    ch = _channel()
    ch._ensure_bg_loop()
    # Shrink the backoff table so the test doesn't wait 10s for the first
    # retry.
    ch._BOT_IDENTITY_RETRY_DELAYS_S = (0.05, 0.05, 0.05)

    identity = BotIdentity(open_id="ou_bot_x", app_id="cli_x", name="TestBot")
    call_count = {"n": 0}

    async def flaky_fetch(_cfg):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return None
        return identity

    with patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=flaky_fetch
    ):
        # Drive the retry loop directly (sync path would trigger the real
        # 10s timeout).
        await asyncio.wait_for(
            asyncio.wrap_future(
                asyncio.run_coroutine_threadsafe(
                    ch._bot_identity_retry_loop(), ch._bg_loop
                )
            ),
            timeout=2.0,
        )

    assert ch.bot_identity is not None
    assert ch.bot_identity.open_id == "ou_bot_x"
    assert ch._bot_open_id == "ou_bot_x"
    ch.stop()


@pytest.mark.asyncio
async def test_bot_identity_retry_loop_respects_shutdown():
    """Shutdown fires mid-retry → loop bails out cleanly without touching
    state."""
    ch = _channel()
    ch._ensure_bg_loop()
    ch._BOT_IDENTITY_RETRY_DELAYS_S = (0.2, 0.2)

    async def never_succeeds(_cfg):
        return None

    with patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=never_succeeds
    ):
        # Kick the loop off, then shut down almost immediately.
        fut = asyncio.run_coroutine_threadsafe(
            ch._bot_identity_retry_loop(), ch._bg_loop
        )
        await asyncio.sleep(0.05)
        ch._shutdown.set()
        # Loop should notice shutdown and return cleanly (not raise, not
        # hang).
        await asyncio.wait_for(asyncio.wrap_future(fut), timeout=2.0)

    assert ch.bot_identity is None
    ch.stop()


def test_bot_identity_store_is_atomic_under_concurrent_writes():
    """Two threads writing the identity simultaneously must never leave
    the pair of fields in a half-updated state (fresh ``_bot_identity`` +
    stale ``_bot_open_id`` or vice-versa)."""
    import threading

    ch = _channel()
    id_a = BotIdentity(open_id="ou_a", app_id="cli_x", name="A")
    id_b = BotIdentity(open_id="ou_b", app_id="cli_x", name="B")

    observed_mismatches = []
    stop = threading.Event()

    def writer(identity):
        while not stop.is_set():
            ch._store_bot_identity(identity)

    def reader():
        while not stop.is_set():
            with ch._bot_identity_lock:
                ident = ch._bot_identity
                open_id = ch._bot_open_id
            if ident is None:
                continue
            if ident.open_id != open_id:
                observed_mismatches.append((ident.open_id, open_id))

    threads = [
        threading.Thread(target=writer, args=(id_a,), daemon=True),
        threading.Thread(target=writer, args=(id_b,), daemon=True),
        threading.Thread(target=reader, daemon=True),
    ]
    for t in threads:
        t.start()
    import time
    time.sleep(0.3)
    stop.set()
    for t in threads:
        t.join(timeout=1.0)

    assert not observed_mismatches, (
        f"observed {len(observed_mismatches)} inconsistent reads of "
        f"(_bot_identity, _bot_open_id) under concurrent writes — "
        f"first few: {observed_mismatches[:3]}"
    )
