"""Tests for the OutboundConfig.on_oversize hook."""

import pytest

from lark_oapi.channel import OutboundConfig, OversizeContext


def test_on_oversize_default_is_none():
    cfg = OutboundConfig()
    assert cfg.on_oversize is None


def test_on_oversize_accepts_callable():
    async def hook(ctx: OversizeContext):
        return None

    cfg = OutboundConfig(on_oversize=hook)
    assert cfg.on_oversize is hook


def test_oversize_context_fields():
    ctx = OversizeContext(
        text="...",
        chat_id="oc_x",
        receive_id_type="chat_id",
        estimated_chunks=5,
    )
    assert ctx.text == "..."
    assert ctx.chat_id == "oc_x"
    assert ctx.receive_id_type == "chat_id"
    assert ctx.estimated_chunks == 5


# --- Integration: hook is invoked before chunking ------------------------

from lark_oapi.channel import FeishuChannel


def _make_channel_with_hook(hook):
    """Build a channel whose driver is a no-op send that captures payloads."""
    cfg = OutboundConfig(text_chunk_limit=20, on_oversize=hook)
    ch = FeishuChannel(app_id="cli_x", app_secret="x", outbound=cfg)
    return ch


@pytest.mark.asyncio
async def test_hook_returns_replacement_sends_one_message(monkeypatch):
    """When hook returns non-empty, exactly one send call carries the replacement."""
    captured = []

    async def fake_create(*args, **kwargs):
        captured.append(kwargs.get("content") or args)
        return {"code": 0, "data": {"message_id": "om_1"}}

    async def hook(ctx: OversizeContext):
        return f"long content: see {ctx.estimated_chunks} chunks at /paste/abc"

    ch = _make_channel_with_hook(hook)
    monkeypatch.setattr(ch._sender._driver, "create_message", fake_create)

    long_text = "x" * 200  # 10x the chunk limit, would normally split into ~10
    result = await ch.send("oc_x", {"text": long_text})

    assert result.success
    assert len(captured) == 1
    payload = captured[0]
    assert "/paste/abc" in str(payload)
    assert "x" * 100 not in str(payload)


@pytest.mark.asyncio
async def test_hook_returns_none_falls_back_to_chunks(monkeypatch):
    """When hook returns None, SDK chunks normally and sends multiple messages."""
    captured = []

    async def fake_create(*args, **kwargs):
        captured.append(kwargs.get("content") or args)
        return {"code": 0, "data": {"message_id": f"om_{len(captured)}"}}

    async def hook(ctx):
        return None

    ch = _make_channel_with_hook(hook)
    monkeypatch.setattr(ch._sender._driver, "create_message", fake_create)

    long_text = "x" * 200
    await ch.send("oc_x", {"text": long_text})

    # 200 chars at limit=20 yields >1 chunk
    assert len(captured) > 1


@pytest.mark.asyncio
async def test_hook_returns_empty_string_falls_back(monkeypatch):
    captured = []

    async def fake_create(*args, **kwargs):
        captured.append(kwargs)
        return {"code": 0, "data": {"message_id": "om_1"}}

    async def hook(ctx):
        return ""

    ch = _make_channel_with_hook(hook)
    monkeypatch.setattr(ch._sender._driver, "create_message", fake_create)
    await ch.send("oc_x", {"text": "x" * 200})
    assert len(captured) > 1


@pytest.mark.asyncio
async def test_hook_raises_propagates_no_fallback(monkeypatch):
    sent = []

    async def fake_create(*args, **kwargs):
        sent.append(kwargs)
        return {"code": 0}

    async def hook(ctx):
        raise RuntimeError("paste.rs unavailable")

    ch = _make_channel_with_hook(hook)
    monkeypatch.setattr(ch._sender._driver, "create_message", fake_create)

    with pytest.raises(RuntimeError, match="paste.rs unavailable"):
        await ch.send("oc_x", {"text": "x" * 200})
    # Crucially, no chunked send happened either:
    assert sent == []


@pytest.mark.asyncio
async def test_short_text_does_not_invoke_hook(monkeypatch):
    invocations = []

    async def hook(ctx):
        invocations.append(ctx)
        return None

    async def fake_create(*args, **kwargs):
        return {"code": 0, "data": {"message_id": "om_1"}}

    ch = _make_channel_with_hook(hook)
    monkeypatch.setattr(ch._sender._driver, "create_message", fake_create)
    await ch.send("oc_x", {"text": "short"})
    assert invocations == []
