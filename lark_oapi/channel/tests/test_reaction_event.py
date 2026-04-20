"""Regression: reaction event field path + 'own' / 'all' filter.

The real `P2ImMessageReactionCreatedV1Data` exposes `user_id: UserId`, not
`operator_id`. Drives the event through `_handle_reaction_event` with a
real model instantiated from a realistic JSON payload.
"""

import time

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
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
