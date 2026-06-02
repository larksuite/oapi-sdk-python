"""Unit tests for the new safety/ module."""

import asyncio
import time
from typing import List

import pytest

from lark_oapi.channel.config import PolicyConfig, GroupOverride
from lark_oapi.channel.safety import (
    ChatPipeline,
    PolicyGate,
    ProcessingLock,
    RejectEvent,
    SafetyPipeline,
    SeenCache,
    TextBatchConfig,
    is_stale,
    merge_batch,
)
from lark_oapi.channel.types import (
    Conversation,
    Identity,
    InboundMessage,
    Mention,
    TextContent,
)


# ---- stale_detector --------------------------------------------------------


def test_is_stale_recent_false():
    now_ms = int(time.time() * 1000)
    assert is_stale(now_ms - 1000) is False


def test_is_stale_old_true():
    now_ms = int(time.time() * 1000)
    assert is_stale(now_ms - 35 * 60_000) is True


def test_is_stale_zero_returns_false():
    assert is_stale(0) is False


# ---- seen_cache ------------------------------------------------------------


@pytest.mark.asyncio
async def test_seen_cache_basic():
    s = SeenCache()
    assert await s.has("a") is False
    await s.add("a")
    assert await s.has("a") is True


def test_seen_cache_lru_bounded():
    s = SeenCache(max_entries=3)
    for k in "abcd":
        s.add_sync(k)
    assert s.has_sync("a") is False  # evicted
    assert s.has_sync("d") is True


def test_seen_cache_falls_back_to_external():
    """If memory misses but external cache hits, it should back-fill."""

    class FakeCache:
        def __init__(self):
            self.store = {"channel:seen:x": "1"}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value, expire=None):
            self.store[key] = value

    fake = FakeCache()
    s = SeenCache(cache=fake)
    assert s.has_sync("x") is True  # not in memory but in fake cache
    assert s.has_sync("x") is True  # now back-filled to memory


# ---- processing_lock -------------------------------------------------------


def test_processing_lock_acquire_and_release():
    lock = ProcessingLock()
    assert lock.acquire("id1") is True
    assert lock.acquire("id1") is False  # still held
    lock.release("id1")
    assert lock.acquire("id1") is True


def test_processing_lock_ttl_expires():
    lock = ProcessingLock(ttl_ms=50)
    assert lock.acquire("id1") is True
    time.sleep(0.08)
    assert lock.acquire("id1") is True  # expired → fresh lock


# ---- policy_gate -----------------------------------------------------------


def _msg(**kw) -> InboundMessage:
    return InboundMessage(
        id=kw.get("id", "om1"),
        create_time=int(time.time() * 1000),
        conversation=Conversation(
            chat_id=kw.get("chat_id", "oc_1"),
            chat_type=kw.get("chat_type", "p2p"),
        ),
        sender=Identity(open_id=kw.get("sender", "ou_sender")),
        mentions=kw.get("mentions", []),
        mentioned_all=kw.get("mentioned_all", False),
        content=TextContent(text=kw.get("text", "hi")),
    )


def test_policy_gate_dm_open_allows():
    gate = PolicyGate(PolicyConfig(dm_policy="open"))
    assert gate.evaluate(_msg()).allowed is True


def test_policy_gate_dm_disabled_reasons():
    gate = PolicyGate(PolicyConfig(dm_policy="disabled"))
    d = gate.evaluate(_msg())
    assert d.allowed is False
    assert d.reason == "policy_dm_disabled"


def test_policy_gate_group_no_mention():
    gate = PolicyGate(PolicyConfig(require_mention=True))
    gate.set_bot_open_id("ou_bot")
    d = gate.evaluate(_msg(chat_type="group"))
    assert d.allowed is False
    assert d.reason == "policy_no_mention"


def test_policy_gate_group_mention_bot():
    gate = PolicyGate(PolicyConfig(require_mention=True))
    gate.set_bot_open_id("ou_bot")
    d = gate.evaluate(_msg(chat_type="group", mentions=[Mention(key="@_bot", open_id="ou_bot")]))
    assert d.allowed is True


def test_policy_gate_group_mention_all_blocked():
    gate = PolicyGate(PolicyConfig(require_mention=True, respond_to_mention_all=False))
    gate.set_bot_open_id("ou_bot")
    d = gate.evaluate(_msg(chat_type="group", mentioned_all=True))
    assert d.allowed is False
    # "policy_no_mention" hits first because the @-all isn't the bot
    assert d.reason == "policy_no_mention"


def test_policy_gate_update_policy_runtime():
    gate = PolicyGate(PolicyConfig(dm_policy="open"))
    assert gate.evaluate(_msg()).allowed is True
    gate.update_policy(dm_policy="disabled")
    assert gate.evaluate(_msg()).allowed is False


def test_policy_gate_group_allowlist():
    gate = PolicyGate(PolicyConfig(group_policy="allowlist", group_allowlist=["oc_ok"], require_mention=False))
    assert gate.evaluate(_msg(chat_type="group", chat_id="oc_ok")).allowed is True
    d = gate.evaluate(_msg(chat_type="group", chat_id="oc_other"))
    assert d.allowed is False
    assert d.reason == "policy_group_not_in_allowlist"


def test_policy_gate_group_override_disables():
    gate = PolicyGate(PolicyConfig(
        group_overrides={"oc_X": GroupOverride(enabled=False)},
    ))
    d = gate.evaluate(_msg(chat_type="group", chat_id="oc_X"))
    assert d.allowed is False


# ---- merge_batch -----------------------------------------------------------


def test_merge_batch_single_returns_unchanged():
    m = _msg(text="one")
    merged = merge_batch([m])
    assert merged is m


def test_merge_batch_multiple_joins_text():
    a = _msg(id="a", text="帮我")
    b = _msg(id="b", text="写一个")
    c = _msg(id="c", text="快排")
    merged = merge_batch([a, b, c])
    assert merged.id == "c"  # last wins
    assert "帮我" in merged.content.text
    assert "写一个" in merged.content.text
    assert "快排" in merged.content.text


# ---- chat_pipeline ---------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_pipeline_debounces_and_merges():
    loop = asyncio.get_running_loop()
    pipeline = ChatPipeline(
        "oc_x",
        TextBatchConfig(delay_ms=50, max_messages=10, max_chars=10_000),
        loop,
    )
    merged_captured: List[InboundMessage] = []

    async def handler(merged, sources):
        merged_captured.append(merged)

    pipeline.push(_msg(id="1", text="hello"), handler)
    pipeline.push(_msg(id="2", text="world"), handler)
    # Wait for debounce
    await asyncio.sleep(0.1)
    await pipeline.dispose()
    assert len(merged_captured) == 1
    assert "hello" in merged_captured[0].content.text
    assert "world" in merged_captured[0].content.text


@pytest.mark.asyncio
async def test_chat_pipeline_flush_on_max_messages():
    loop = asyncio.get_running_loop()
    pipeline = ChatPipeline(
        "oc_x",
        TextBatchConfig(delay_ms=5000, max_messages=2, max_chars=10_000),
        loop,
    )
    merged_captured: List[InboundMessage] = []

    async def handler(merged, sources):
        merged_captured.append(merged)

    pipeline.push(_msg(id="1", text="a"), handler)
    pipeline.push(_msg(id="2", text="b"), handler)  # triggers max_messages flush
    await asyncio.sleep(0.02)
    await pipeline.dispose()
    assert len(merged_captured) == 1


@pytest.mark.asyncio
async def test_chat_pipeline_run_chains_serially():
    loop = asyncio.get_running_loop()
    pipeline = ChatPipeline("x", TextBatchConfig(), loop, serial_only=True)
    log: List[str] = []

    async def make_task(name: str, delay: float):
        async def task():
            log.append(f"{name}:start")
            await asyncio.sleep(delay)
            log.append(f"{name}:end")

        return task

    t1 = await make_task("A", 0.05)
    t2 = await make_task("B", 0.01)
    r1 = pipeline.run(t1)
    r2 = pipeline.run(t2)
    await asyncio.gather(r1, r2)
    assert log == ["A:start", "A:end", "B:start", "B:end"]


# ---- SafetyPipeline integration --------------------------------------------


@pytest.mark.asyncio
async def test_safety_pipeline_drops_stale():
    loop = asyncio.get_running_loop()
    got: List[InboundMessage] = []

    async def on_msg(m):
        got.append(m)

    sp = SafetyPipeline(loop=loop, on_message=on_msg, policy=PolicyConfig(dm_policy="open"))
    old = _msg()
    old.create_time = int((time.time() - 3600) * 1000)  # 1h old
    await sp.push_message(old)
    await asyncio.sleep(0.05)
    assert got == []


@pytest.mark.asyncio
async def test_safety_pipeline_dedup():
    loop = asyncio.get_running_loop()
    got = []

    async def on_msg(m):
        got.append(m)

    sp = SafetyPipeline(loop=loop, on_message=on_msg, policy=PolicyConfig(dm_policy="open"),
                        batch_config=TextBatchConfig(delay_ms=0))
    m1 = _msg(id="o1")
    await sp.push_message(m1)
    await asyncio.sleep(0.05)
    await sp.push_message(m1)  # duplicate
    await asyncio.sleep(0.05)
    assert len(got) == 1


@pytest.mark.asyncio
async def test_safety_pipeline_emits_reject():
    loop = asyncio.get_running_loop()
    rejected: List[RejectEvent] = []

    async def on_msg(m):
        pass

    sp = SafetyPipeline(
        loop=loop,
        on_message=on_msg,
        on_reject=lambda e: rejected.append(e),
        policy=PolicyConfig(dm_policy="disabled"),
    )
    await sp.push_message(_msg())
    await asyncio.sleep(0.02)
    assert len(rejected) == 1
    assert rejected[0].reason == "policy_dm_disabled"


@pytest.mark.asyncio
async def test_safety_pipeline_batches_rapid_messages():
    loop = asyncio.get_running_loop()
    got: List[InboundMessage] = []

    async def on_msg(m):
        got.append(m)

    sp = SafetyPipeline(
        loop=loop,
        on_message=on_msg,
        policy=PolicyConfig(dm_policy="open"),
        batch_config=TextBatchConfig(delay_ms=50, max_messages=10, max_chars=10_000),
    )
    await sp.push_message(_msg(id="1", text="帮我"))
    await sp.push_message(_msg(id="2", text="写一个"))
    await sp.push_message(_msg(id="3", text="快排"))
    await asyncio.sleep(0.15)
    assert len(got) == 1
    assert "帮我" in got[0].content.text
    assert "快排" in got[0].content.text


@pytest.mark.asyncio
async def test_safety_pipeline_processing_lock_blocks_concurrent():
    loop = asyncio.get_running_loop()
    call_count = 0
    enter_event = asyncio.Event()
    proceed = asyncio.Event()

    async def on_msg(m):
        nonlocal call_count
        call_count += 1
        enter_event.set()
        await proceed.wait()

    sp = SafetyPipeline(
        loop=loop,
        on_message=on_msg,
        policy=PolicyConfig(dm_policy="open"),
        batch_config=TextBatchConfig(delay_ms=0),
    )
    # First push — handler runs and awaits `proceed`
    await sp.push_message(_msg(id="o1"))
    await enter_event.wait()
    # Second push of same id while handler is still running — lock blocks
    await sp.push_message(_msg(id="o1"))
    await asyncio.sleep(0.05)
    proceed.set()
    await asyncio.sleep(0.05)
    assert call_count == 1
