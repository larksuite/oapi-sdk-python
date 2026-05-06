"""Cover the 3 tiers of SafetyPipeline (push_message / push_action / push_light)."""

import asyncio
from typing import List

import pytest

from lark_oapi.channel.config import PolicyConfig
from lark_oapi.channel.safety import RejectEvent, SafetyPipeline
from lark_oapi.channel.safety.types import TextBatchConfig


# ---- push_action (tier 2) ----------------------------------------------


@pytest.mark.asyncio
async def test_push_action_runs_handler_once():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    calls: List[int] = []

    async def handler():
        calls.append(1)

    await sp.push_action(event_id="ev_1", queue_scope="oc_1", handler=handler)
    await asyncio.sleep(0.05)
    assert calls == [1]


@pytest.mark.asyncio
async def test_push_action_dedupes_duplicate_event():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    calls: List[int] = []

    async def handler():
        calls.append(1)

    await sp.push_action(event_id="ev_same", queue_scope="oc_1", handler=handler)
    await asyncio.sleep(0.05)
    await sp.push_action(event_id="ev_same", queue_scope="oc_1", handler=handler)
    await asyncio.sleep(0.05)
    assert calls == [1]  # second was dropped


@pytest.mark.asyncio
async def test_push_action_serial_queue_preserves_order():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    order: List[str] = []

    async def slow():
        order.append("slow-start")
        await asyncio.sleep(0.05)
        order.append("slow-end")

    async def fast():
        order.append("fast-start")
        order.append("fast-end")

    await sp.push_action("ev_A", "oc_scope", slow)
    await sp.push_action("ev_B", "oc_scope", fast)
    await asyncio.sleep(0.2)
    assert order == ["slow-start", "slow-end", "fast-start", "fast-end"]


@pytest.mark.asyncio
async def test_push_action_handler_exception_is_logged_not_raised():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)

    async def bad():
        raise RuntimeError("oops")

    # Should not raise at push time
    await sp.push_action("ev_x", "oc_x", bad)
    await asyncio.sleep(0.05)


# ---- push_light (tier 3) ------------------------------------------------


@pytest.mark.asyncio
async def test_push_light_runs_handler():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    calls: List[int] = []

    async def h():
        calls.append(1)

    await sp.push_light("ev_l", h)
    assert calls == [1]


@pytest.mark.asyncio
async def test_push_light_dedupes():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    calls: List[int] = []

    async def h():
        calls.append(1)

    await sp.push_light("ev_same", h)
    await sp.push_light("ev_same", h)
    assert calls == [1]


@pytest.mark.asyncio
async def test_push_light_sync_handler_accepted():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    calls: List[int] = []

    def h():
        calls.append(1)

    await sp.push_light("ev_sync", h)
    assert calls == [1]


@pytest.mark.asyncio
async def test_push_light_handler_exception_swallowed():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)

    async def bad():
        raise ValueError("x")

    await sp.push_light("ev_bad", bad)  # no raise


# ---- queue disabled / direct dispatch path -----------------------------


@pytest.mark.asyncio
async def test_message_pipeline_direct_dispatch_when_queue_disabled():
    from lark_oapi.channel.safety.types import ChatQueueConfig

    loop = asyncio.get_running_loop()
    got = []

    async def on_msg(m):
        got.append(m)

    sp = SafetyPipeline(
        loop=loop,
        on_message=on_msg,
        policy=PolicyConfig(dm_policy="open"),
        queue_config=ChatQueueConfig(enabled=False),
        batch_config=TextBatchConfig(delay_ms=0),
    )
    from lark_oapi.channel.types import Conversation, Identity, InboundMessage, TextContent
    import time
    msg = InboundMessage(
        id="om_direct", create_time=int(time.time() * 1000),
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_s"),
        content=TextContent(text="x"),
    )
    await sp.push_message(msg)
    assert len(got) == 1


# ---- dispose drains --------------------------------------------------------


@pytest.mark.asyncio
async def test_dispose_clears_pipelines():
    loop = asyncio.get_running_loop()
    sp = SafetyPipeline(loop=loop, on_message=lambda m: None)
    await sp.push_action("e", "scope", lambda: None)
    await asyncio.sleep(0.05)
    await sp.dispose()


# ---- on_reject handler can be awaitable ---------------------------------


@pytest.mark.asyncio
async def test_push_message_reject_fires_on_reject_handler():
    from lark_oapi.channel.types import Conversation, Identity, InboundMessage, TextContent
    import time

    loop = asyncio.get_running_loop()
    rejected: List[RejectEvent] = []

    sp = SafetyPipeline(
        loop=loop,
        on_message=lambda m: None,
        on_reject=lambda e: rejected.append(e),
        policy=PolicyConfig(dm_policy="disabled"),
    )
    msg = InboundMessage(
        id="om_r", create_time=int(time.time() * 1000),
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_s"),
        content=TextContent(text="x"),
    )
    await sp.push_message(msg)
    await asyncio.sleep(0.02)
    assert len(rejected) == 1 and rejected[0].reason == "policy_dm_disabled"
