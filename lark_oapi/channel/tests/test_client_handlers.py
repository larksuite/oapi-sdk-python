"""FeishuChannel's per-event async handlers — exercised with fake P2 payloads.

Drives `_handle_*_event` directly, bypassing the WS / dispatcher layer.
Uses the node-aligned `channel.on("event_name", handler)` registration API.
"""

import json
from types import SimpleNamespace

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
from lark_oapi.channel.safety import RejectEvent
from lark_oapi.api.im.v1.model.p2_im_message_reaction_created_v1 import (
    P2ImMessageReactionCreatedV1,
)
from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTrigger


def _client():
    return _ChannelClient(app_id="cli_x", app_secret="s")


# ---- interaction handler -------------------------------------------------


def _fake_card_action(*, action_value, tag="button", message_id="om_xyz",
                      operator_open_id="ou_op"):
    """SimpleNamespace mimicking P2CardActionTrigger attribute tree (bypasses
    the generated model's strict typing that forbids string action.value)."""
    return SimpleNamespace(
        event=SimpleNamespace(
            action=SimpleNamespace(tag=tag, value=action_value),
            operator=SimpleNamespace(open_id=operator_open_id),
            context=SimpleNamespace(open_message_id=message_id),
        ),
    )


@pytest.mark.asyncio
async def test_handle_interaction_event_passes_parsed_action():
    c = _client()
    got = []
    c.on("cardAction", lambda event: got.append(event))
    data = _fake_card_action(action_value=json.dumps({"kind": "rate", "score": "up"}))
    await c._handle_interaction_event(data)
    assert len(got) == 1
    event = got[0]
    assert event.action.value == {"kind": "rate", "score": "up"}
    assert event.message_id == "om_xyz"
    assert event.operator.open_id == "ou_op"
    assert event.action.tag == "button"


@pytest.mark.asyncio
async def test_handle_interaction_event_non_json_value_wrapped():
    c = _client()
    got = []
    c.on("cardAction", lambda event: got.append(event))
    data = _fake_card_action(action_value="plain-string-not-json")
    await c._handle_interaction_event(data)
    assert got[0].action.value == {"value": "plain-string-not-json"}


@pytest.mark.asyncio
async def test_handle_interaction_event_no_handler_is_noop():
    c = _client()
    # No cardAction handler registered — shouldn't raise
    data = P2CardActionTrigger({"event": {}})
    await c._handle_interaction_event(data)


# ---- reaction handler ---------------------------------------------------


@pytest.mark.asyncio
async def test_handle_reaction_event_off_mode_drops():
    c = _client()
    c._config.inbound.reaction_notifications = "off"
    got = []
    c.on("reaction", lambda event: got.append(event))
    data = P2ImMessageReactionCreatedV1({
        "event": {
            "message_id": "om_1",
            "reaction_type": {"emoji_type": "HEART"},
            "user_id": {"open_id": "ou_r"},
        },
    })
    await c._handle_reaction_event(data, action="create")
    assert got == []


# ---- bot add / leave handlers -------------------------------------------


@pytest.mark.asyncio
async def test_handle_bot_event_join_dispatches():
    c = _client()
    got = []
    c.on("botAdded", lambda event: got.append(event))

    data = SimpleNamespace(
        event=SimpleNamespace(
            chat_id="oc_new",
            operator_id=SimpleNamespace(open_id="ou_op"),
        ),
    )
    await c._handle_bot_event(data, joined=True)
    assert len(got) == 1
    assert got[0].chat_id == "oc_new"
    assert got[0].operator.open_id == "ou_op"


@pytest.mark.asyncio
async def test_handle_bot_event_leave_dispatches_when_handler_set():
    c = _client()
    got = []
    c.on("botLeave", lambda event: got.append(event))

    data = SimpleNamespace(
        event=SimpleNamespace(chat_id="oc_gone", operator_id=None),
    )
    await c._handle_bot_event(data, joined=False)
    assert len(got) == 1


@pytest.mark.asyncio
async def test_handle_bot_event_no_handler_noop():
    c = _client()
    data = SimpleNamespace(event=SimpleNamespace(chat_id="oc_x", operator_id=None))
    await c._handle_bot_event(data, joined=True)  # no raise


# ---- message_read handler -----------------------------------------------


@pytest.mark.asyncio
async def test_handle_message_read_event_dispatches():
    c = _client()
    got = []
    c.on("messageRead", lambda event: got.append(event))
    data = SimpleNamespace(event=SimpleNamespace(
        reader=SimpleNamespace(reader_id=SimpleNamespace(open_id="ou_reader")),
        message_id_list=["om_1", "om_2"],
    ))
    await c._handle_message_read_event(data)
    assert len(got) == 1
    assert got[0].message_ids == ["om_1", "om_2"]
    assert got[0].reader.open_id == "ou_reader"


# ---- require_user_auth error paths --------------------------------------


@pytest.mark.asyncio
async def test_require_user_auth_raises_when_scope_blocked():
    from lark_oapi.channel.errors import UATAuthError

    c = _client()
    c._config.uat.blocked_scopes = ["im:admin"]
    with pytest.raises(UATAuthError):
        await c.require_user_auth("ou_user", ["im:admin"])


@pytest.mark.asyncio
async def test_require_user_auth_raises_when_scope_not_allowed():
    from lark_oapi.channel.errors import UATAuthError

    c = _client()
    c._config.uat.allowed_scopes = ["im:message"]
    with pytest.raises(UATAuthError):
        await c.require_user_auth("ou_user", ["wiki:write"])


@pytest.mark.asyncio
async def test_require_user_auth_returns_existing_uat_when_fresh():
    import time
    from lark_oapi.channel.types import UAT

    c = _client()
    fresh = UAT(
        access_token="t",
        refresh_token="r",
        expires_at=time.time() + 3600,
        scopes=["im:message"],
    )
    await c._token_store.set("ou_me", fresh)
    got = await c.require_user_auth("ou_me", ["im:message"])
    assert got is fresh


# ---- dispatcher property builds lazily ----------------------------------


def test_dispatcher_property_builds_lazily():
    c = _client()
    assert c._dispatcher is None
    d = c.dispatcher
    assert d is not None
    assert c._dispatcher is d


# ---- _emit_reject with exception in handler is logged, not raised -------


def test_emit_reject_handler_exception_is_swallowed(caplog):
    c = _client()

    def bad(_):
        raise ValueError("handler bug")

    c.on("reject", bad)
    c._emit_reject(RejectEvent(
        message_id="om_x", chat_id="oc_1", sender_id="ou_1", reason="policy_no_mention",
    ))
    assert any("raised" in (r.message or "") for r in caplog.records)
