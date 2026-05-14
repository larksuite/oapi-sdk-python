"""Every inbound handler must route through the right ``SafetyPipeline`` tier:

    * cardAction  → ``push_action`` (tier 2, dedup + lock + queue by chatId)
    * reaction    → ``push_light``  (tier 3, dedup only)
    * comment     → ``push_action`` (tier 2, dedup + lock + queue by fileToken)

This guards against bypassing the safety tiers and accidentally allowing
redelivered events to double-fire user handlers.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.config import ChannelConfig, InboundConfig


def _client(reaction_notifications: str = "all") -> FeishuChannel:
    # Default inbound.reaction_notifications is "own" — i.e. the channel
    # ignores reactions on messages it didn't send. For routing assertions
    # we want every reaction to fall through to the safety pipeline, so
    # override to "all".
    c = FeishuChannel(
        app_id="cli_test",
        app_secret="sec",
        config=ChannelConfig(
            inbound=InboundConfig(reaction_notifications=reaction_notifications),
        ),
    )
    c._ensure_bg_loop()
    return c


def _installed_safety(channel: FeishuChannel):
    """Install AsyncMocks for push_action / push_light on a channel that
    hasn't been ``connect()``-ed, so the handlers see a non-None safety
    and take the safe path instead of the fallback direct-invoke."""
    safety = SimpleNamespace(
        push_action=AsyncMock(),
        push_light=AsyncMock(),
    )
    channel._safety = safety  # type: ignore[assignment]
    return safety


# ---------------------------------------------------------------------------
# cardAction → push_action
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_card_action_routes_through_push_action():
    c = _client()
    safety = _installed_safety(c)

    action = SimpleNamespace(tag="button", value={"name": "confirm", "id": 7})
    context = SimpleNamespace(open_message_id="om_1", open_chat_id="oc_1")
    operator = SimpleNamespace(open_id="ou_u")
    event = SimpleNamespace(action=action, context=context, operator=operator)
    data = SimpleNamespace(event=event)

    await c._handle_interaction_event(data)

    assert safety.push_action.await_count == 1
    event_id, scope, _handler = safety.push_action.await_args.args
    assert event_id.startswith("card:om_1:ou_u:")
    # stable action identity includes tag and JSON-sorted value
    assert "button:" in event_id
    assert '"id": 7' in event_id and '"name": "confirm"' in event_id
    assert scope == "oc_1"
    # tier 3 must not be touched
    assert safety.push_light.await_count == 0


@pytest.mark.asyncio
async def test_card_action_fallback_without_safety_still_invokes():
    """If the pipeline hasn't been built yet (early event, unit test
    bypassing connect), the handler must still fire — just without
    dedup/lock protection."""
    # Fresh channel, do NOT call _ensure_bg_loop → _safety stays None.
    c = FeishuChannel(app_id="cli_test", app_secret="sec")
    assert c._safety is None
    calls: list = []

    def _on(evt):
        calls.append(evt)

    c.on("cardAction", _on)

    action = SimpleNamespace(tag="button", value=None)
    context = SimpleNamespace(open_message_id="om_x", open_chat_id="oc_x")
    operator = SimpleNamespace(open_id="ou_x")
    event = SimpleNamespace(action=action, context=context, operator=operator)
    data = SimpleNamespace(event=event)

    await c._handle_interaction_event(data)
    assert len(calls) == 1
    assert calls[0].message_id == "om_x"


# ---------------------------------------------------------------------------
# reaction → push_light
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reaction_added_routes_through_push_light():
    c = _client()
    safety = _installed_safety(c)

    data = SimpleNamespace(event=SimpleNamespace(
        user_id=SimpleNamespace(open_id="ou_r"),
        message_id="om_m",
        reaction_type=SimpleNamespace(emoji_type="THUMBSUP"),
        action_time="1777000000",
    ))

    await c._handle_reaction_event(data, action="create")

    assert safety.push_light.await_count == 1
    event_id, _handler = safety.push_light.await_args.args
    assert event_id == "reaction:om_m:ou_r:THUMBSUP:added"
    assert safety.push_action.await_count == 0


@pytest.mark.asyncio
async def test_reaction_removed_event_id_distinguishes_direction():
    """Same message + user + emoji but add vs remove must dedup separately,
    otherwise an add immediately followed by a remove would drop one."""
    c = _client()
    safety = _installed_safety(c)

    data = SimpleNamespace(event=SimpleNamespace(
        user_id=SimpleNamespace(open_id="ou_r"),
        message_id="om_m",
        reaction_type=SimpleNamespace(emoji_type="THUMBSUP"),
        action_time=None,
    ))

    await c._handle_reaction_event(data, action="create")
    await c._handle_reaction_event(data, action="delete")

    calls = [a.args[0] for a in safety.push_light.await_args_list]
    assert calls == [
        "reaction:om_m:ou_r:THUMBSUP:added",
        "reaction:om_m:ou_r:THUMBSUP:removed",
    ]


# ---------------------------------------------------------------------------
# comment → push_action
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_comment_routes_through_push_action_scoped_by_file_token():
    c = _client()
    safety = _installed_safety(c)

    # Realistic ``drive.notice.comment_add_v1`` wire shape.
    data = SimpleNamespace(event={
        "file_token": "doc_abc",
        "file_type": "docx",
        "comment_id": "cmt_99",
        "is_mentioned": True,
        "create_time": "1700000000000",
        "notice_meta": {
            "from_user_id": {"open_id": "ou_o"},
            "is_mentioned": True,
            "timestamp": "1700000000000",
        },
    })

    await c._handle_comment_event(data)

    assert safety.push_action.await_count == 1
    event_id, scope, _handler = safety.push_action.await_args.args
    assert event_id == "comment:doc_abc:cmt_99"
    assert scope == "doc_abc"
    assert safety.push_light.await_count == 0


@pytest.mark.asyncio
async def test_comment_without_file_token_is_dropped_before_safety():
    """normalize_comment returns None for malformed payloads; safety must
    not be invoked with empty event_id / scope (which would collide
    across unrelated null events and cause cross-event dedup)."""
    c = _client()
    safety = _installed_safety(c)

    # Missing file_token → normalize_comment returns None
    data = SimpleNamespace(event={"comment_id": "cmt_x"})
    await c._handle_comment_event(data)

    assert safety.push_action.await_count == 0
