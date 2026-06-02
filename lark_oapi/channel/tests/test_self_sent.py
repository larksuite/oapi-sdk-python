"""Self-sent message filter tests."""

import asyncio
import time

import pytest

from lark_oapi.channel.config import InboundConfig, TextBatchConfig
from lark_oapi.channel.safety import SafetyPipeline
from lark_oapi.channel.types import (
    Conversation,
    Identity,
    InboundMessage,
    TextContent,
)

BOT = "ou_bot"
USER = "ou_user"


def _msg(sender: str, *, message_id: str = "m1") -> InboundMessage:
    return InboundMessage(
        id=message_id,
        create_time=int(time.time() * 1000),
        conversation=Conversation(chat_id="c1", chat_type="p2p"),
        sender=Identity(open_id=sender),
        content=TextContent(text="hi"),
    )


@pytest.mark.asyncio
async def test_self_sent_dropped_by_default():
    loop = asyncio.get_running_loop()
    delivered = []
    rejects = []

    async def on_message(m): delivered.append(m)

    def on_reject(r): rejects.append(r)

    pipe = SafetyPipeline(
        loop=loop,
        on_message=on_message,
        on_reject=on_reject,
        drop_self_sent=True,
    )
    pipe.set_bot_open_id(BOT)
    await pipe.push_message(_msg(BOT))
    await asyncio.sleep(0.05)

    assert delivered == []
    assert len(rejects) == 1 and rejects[0].reason == "self_sent"


@pytest.mark.asyncio
async def test_user_sent_passes_through():
    loop = asyncio.get_running_loop()
    delivered = []

    async def on_message(m): delivered.append(m)

    pipe = SafetyPipeline(
        loop=loop,
        on_message=on_message,
        drop_self_sent=True,
        batch_config=TextBatchConfig(delay_ms=0),
    )
    pipe.set_bot_open_id(BOT)
    await pipe.push_message(_msg(USER))
    await asyncio.sleep(0.05)

    assert len(delivered) == 1


@pytest.mark.asyncio
async def test_self_sent_passes_when_disabled():
    loop = asyncio.get_running_loop()
    delivered = []

    async def on_message(m): delivered.append(m)

    pipe = SafetyPipeline(
        loop=loop,
        on_message=on_message,
        drop_self_sent=False,
        batch_config=TextBatchConfig(delay_ms=0),
    )
    pipe.set_bot_open_id(BOT)
    await pipe.push_message(_msg(BOT))
    await asyncio.sleep(0.05)

    assert len(delivered) == 1


@pytest.mark.asyncio
async def test_self_sent_allowed_when_bot_id_unknown():
    """Conservative: don't filter until bot identity is resolved."""
    loop = asyncio.get_running_loop()
    delivered = []

    async def on_message(m): delivered.append(m)

    pipe = SafetyPipeline(
        loop=loop,
        on_message=on_message,
        drop_self_sent=True,
        batch_config=TextBatchConfig(delay_ms=0),
    )
    # set_bot_open_id NOT called — identity unknown
    await pipe.push_message(_msg(BOT))
    await asyncio.sleep(0.05)

    assert len(delivered) == 1


def test_inbound_config_default_drops_self_sent():
    cfg = InboundConfig()
    assert cfg.drop_self_sent is True
