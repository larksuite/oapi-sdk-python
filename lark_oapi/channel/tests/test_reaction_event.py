"""Regression: reaction event field path + 'own' / 'all' filter.

The real `P2ImMessageReactionCreatedV1Data` exposes `user_id: UserId`, not
`operator_id`. Drives the event through `_handle_reaction_event` with a
real model instantiated from a realistic JSON payload.
"""

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
from lark_oapi.channel.types import SendResult
from lark_oapi.api.im.v1.model.p2_im_message_reaction_created_v1 import (
    P2ImMessageReactionCreatedV1,
)

_PAYLOAD = {
    "schema": "2.0",
    "header": {
        "event_id": "e1",
        "token": "tk",
        "app_id": "cli_dummy",
        "tenant_key": "tk",
        "event_type": "im.message.reaction.created_v1",
        "create_time": str(int(time.time() * 1000)),
    },
    "event": {
        "message_id": "om_target",
        "reaction_type": {"emoji_type": "THUMBSUP"},
        "operator_type": "user",
        "user_id": {"union_id": "on_U", "user_id": "u", "open_id": "ou_reactor"},
        "action_time": str(int(time.time() * 1000)),
        "app_id": "cli_dummy",
    },
}


@pytest.mark.asyncio
async def test_reaction_event_reads_open_id_correctly():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._track_sent_message("om_target")

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = P2ImMessageReactionCreatedV1(_PAYLOAD)
    await client._handle_reaction_event(data, action="create")

    assert len(captured) == 1
    e = captured[0]
    assert e.message_id == "om_target"
    assert e.operator.open_id == "ou_reactor"
    assert e.emoji_type == "THUMBSUP"
    assert e.action == "added"


@pytest.mark.asyncio
async def test_reaction_event_uses_sent_chat_context_when_raw_event_omits_chat():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._sender.send = AsyncMock(return_value=SendResult.ok(message_id="om_target"))

    result = await client.send("oc_1", {"text": "hello"}, {"receive_id_type": "chat_id"})
    assert result.success is True

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = P2ImMessageReactionCreatedV1(_PAYLOAD)
    await client._handle_reaction_event(data, action="create")

    assert len(captured) == 1
    assert captured[0].chat_id == "oc_1"
    assert captured[0].chat_type is None


@pytest.mark.asyncio
async def test_reaction_event_does_not_guess_chat_context_for_non_chat_targets():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._sender.send = AsyncMock(return_value=SendResult.ok(message_id="om_target"))

    result = await client.send("ou_1", {"text": "hello"}, {"receive_id_type": "open_id"})
    assert result.success is True

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = P2ImMessageReactionCreatedV1(_PAYLOAD)
    await client._handle_reaction_event(data, action="create")

    assert len(captured) == 1
    assert captured[0].chat_id is None
    assert captured[0].chat_type is None


@pytest.mark.asyncio
async def test_reaction_event_prefers_raw_chat_context_over_sent_context():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._sender.send = AsyncMock(return_value=SendResult.ok(message_id="om_target"))
    await client.send("oc_sent", {"text": "hello"}, {"receive_id_type": "chat_id"})

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = SimpleNamespace(
        event=SimpleNamespace(
            message_id="om_target",
            user_id=SimpleNamespace(open_id="ou_reactor"),
            reaction_type=SimpleNamespace(emoji_type="THUMBSUP"),
            action_time=str(int(time.time() * 1000)),
            chat_id="oc_raw",
            chat_type="group",
        )
    )
    await client._handle_reaction_event(data, action="create")

    assert len(captured) == 1
    assert captured[0].chat_id == "oc_raw"
    assert captured[0].chat_type == "group"


@pytest.mark.asyncio
async def test_reaction_event_tracks_chunk_ids_for_sent_chat_context():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._sender.send = AsyncMock(
        return_value=SendResult.ok(message_id="om_first", chunk_ids=["om_first", "om_second"])
    )
    await client.send("oc_1", {"text": "hello"}, {"receive_id_type": "chat_id"})

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    payload = dict(_PAYLOAD)
    payload["event"] = dict(_PAYLOAD["event"], message_id="om_second")
    data = P2ImMessageReactionCreatedV1(payload)
    await client._handle_reaction_event(data, action="create")

    assert len(captured) == 1
    assert captured[0].message_id == "om_second"
    assert captured[0].chat_id == "oc_1"


@pytest.mark.asyncio
async def test_reaction_own_filter_drops_untracked():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    # No _track_sent_message → reaction on unknown message dropped in 'own' mode.

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = P2ImMessageReactionCreatedV1(_PAYLOAD)
    await client._handle_reaction_event(data, action="create")
    assert captured == []


@pytest.mark.asyncio
async def test_reaction_all_mode_forwards_everything():
    client = _ChannelClient(app_id="cli_dummy", app_secret="s")
    client._config.inbound.reaction_notifications = "all"

    captured = []
    client.on("reaction", lambda event: captured.append(event))

    data = P2ImMessageReactionCreatedV1(_PAYLOAD)
    await client._handle_reaction_event(data, action="create")
    assert len(captured) == 1
