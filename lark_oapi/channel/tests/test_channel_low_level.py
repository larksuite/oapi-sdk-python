"""Low-level FeishuChannel helpers: recall / add_reaction / update_card /
download_resource / disconnect / client accessors."""

from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel


@pytest.fixture
def channel():
    return FeishuChannel(app_id="cli_x", app_secret="s")


@pytest.mark.asyncio
async def test_update_card_calls_underlying_patch(channel):
    channel._driver.patch_message = AsyncMock(return_value={"code": 0})
    r = await channel.update_card("om_1", {"schema": "2.0"})
    assert r.success is True
    channel._driver.patch_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_card_failure_returns_failed_result(channel):
    channel._driver.patch_message = AsyncMock(
        return_value={"code": 230001, "msg": "invalid card"}
    )
    r = await channel.update_card("om_1", {"schema": "2.0"})
    assert r.success is False
    assert r.error is not None
    assert r.error.raw_code == 230001
    assert r.raw == {"code": 230001, "msg": "invalid card"}


@pytest.mark.asyncio
async def test_recall_message_success(channel):
    channel._driver.delete_message = AsyncMock(return_value={"code": 0})
    r = await channel.recall_message("om_2")
    assert r.success is True


@pytest.mark.asyncio
async def test_recall_message_failure_surfaces(channel):
    channel._driver.delete_message = AsyncMock(return_value={"code": 230002, "msg": "not exist"})
    r = await channel.recall_message("om_missing")
    assert r.success is False
    assert r.error is not None


@pytest.mark.asyncio
async def test_add_reaction_success(channel):
    channel._driver.add_reaction = AsyncMock(return_value={"code": 0})
    r = await channel.add_reaction("om_1", "THUMBSUP")
    assert r.success is True


@pytest.mark.asyncio
async def test_remove_reaction_success(channel):
    channel._driver.remove_reaction = AsyncMock(return_value={"code": 0})
    r = await channel.remove_reaction("om_1", "rxn_1")
    assert r.success is True


@pytest.mark.asyncio
async def test_download_resource_delegates_to_hook(channel):
    channel._download_media = AsyncMock(return_value=b"\x89PNG...")
    data = await channel.download_resource("img_xxx", resource_type="image")
    assert data == b"\x89PNG..."


def test_client_exposes_underlying():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    assert channel.client is channel._client


def test_dispatcher_accessor_triggers_build():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    channel._ensure_bg_loop()
    d = channel.dispatcher
    assert d is not None


def test_bot_identity_accessor_default_none():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    assert channel.bot_identity is None


def test_update_policy_syncs_into_channel_config():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    channel._ensure_bg_loop()  # spin safety up
    channel.update_policy(dm_policy="disabled", require_mention=False)
    assert channel.get_policy().dm_policy == "disabled"
    assert channel.get_policy().require_mention is False


@pytest.mark.asyncio
async def test_disconnect_drains_safety_and_stops():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    channel._ensure_bg_loop()
    await channel.disconnect()
    # After disconnect() the bg loop + ws client + thread are torn down,
    # and the started flag is reset so a subsequent connect() can re-run.
    # ``_shutdown`` is cleared at the end of stop() so the channel can be
    # reconnected later; we assert on the
    # observable state that actually matters.
    assert channel._bg_loop is None
    assert channel._ws_client is None
    assert channel._started is False


@pytest.mark.asyncio
async def test_connect_is_idempotent_when_started():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    channel._started = True  # pretend start() already ran
    # Should return quickly without attempting to start WS
    await channel.connect()


@pytest.mark.asyncio
async def test_send_stream_unknown_kind_raises():
    channel = FeishuChannel(app_id="cli_x", app_secret="s")
    with pytest.raises(TypeError):
        await channel.stream("oc_x", {"nonsense": "body"})


@pytest.mark.asyncio
async def test_send_unknown_keys_raises():
    from lark_oapi.channel._coerce import coerce_outbound as _coerce_outbound
    with pytest.raises(TypeError):
        _coerce_outbound({"unknown_key": "x"})


@pytest.mark.asyncio
async def test_send_media_buffer_coercion():
    from lark_oapi.channel._coerce import coerce_outbound as _coerce_outbound
    from lark_oapi.channel.types import OutboundFile
    ob = _coerce_outbound({"file": {"source": b"\x01\x02", "fileName": "f.bin"}})
    assert isinstance(ob, OutboundFile)
    assert ob.source.kind == "buffer"


@pytest.mark.asyncio
async def test_send_media_source_media_ref_passes_through():
    from lark_oapi.channel._coerce import coerce_outbound as _coerce_outbound
    from lark_oapi.channel.types import MediaSource, OutboundImage
    ob = _coerce_outbound({"image": {"source": MediaSource(kind="key", key="img_x")}})
    assert isinstance(ob, OutboundImage)
    assert ob.source.key == "img_x"


@pytest.mark.asyncio
async def test_send_markdown_stream_invokes_producer(channel):
    # MarkdownStream now uses the CardKit preallocation flow — mock the 4
    # channel methods it calls. Verify seq-ordered element updates + finish.
    channel.create_card_instance = AsyncMock(return_value="card_xyz")

    from lark_oapi.channel.types import SendResult as _SR
    channel.send_card_by_reference = AsyncMock(
        return_value=_SR.ok(message_id="om_fake_stream"),
    )
    channel.update_card_element_content = AsyncMock(return_value=None)
    channel.finish_streaming_card = AsyncMock(return_value=None)

    got_controller = []

    async def producer(s):
        got_controller.append(s)
        await s.append("hello")

    result = await channel.stream("oc_1", {"markdown": producer})
    assert result.success is True
    assert result.message_id == "om_fake_stream"
    assert got_controller  # producer ran
    channel.create_card_instance.assert_awaited_once()
    channel.send_card_by_reference.assert_awaited_once()
    channel.finish_streaming_card.assert_awaited_once()
    # At least one element update was issued via the seq-ordered API,
    # NOT via the generic patch API.
    assert channel.update_card_element_content.await_count >= 1
