"""Direct coverage for SeenCache expiry, SSRF resolution, and media reads."""

import asyncio
import socket
import time
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
from lark_oapi.channel.errors import FeishuChannelErrorCode, FeishuChannelError
from lark_oapi.channel.safety import SeenCache
from lark_oapi.channel.outbound.media.ssrf_guard import assert_public_url


# ---- SeenCache: real TTL expiry, not just ttl=0 -----------------------------


@pytest.mark.asyncio
async def test_seen_cache_expires_after_real_ttl():
    cache = SeenCache(ttl_seconds=1, sweep_seconds=0)
    await cache.add("k1")
    assert await cache.has("k1") is True
    # Hard-advance the internal expire time by poking the memory map directly.
    # (We don't want this test to literally sleep >1s.)
    expired_at = time.time() - 1
    cache._memory["k1"] = expired_at
    assert await cache.has("k1") is False


# ---- SSRF via IPv6 resolution path -----------------------------------------


@pytest.mark.asyncio
async def test_ssrf_blocks_ipv6_loopback_resolve():
    """A hostname resolving to `::1` must be blocked."""
    with patch(
            "socket.getaddrinfo",
            return_value=[(socket.AF_INET6, 0, 0, "", ("::1", 0, 0, 0))],
    ):
        with pytest.raises(FeishuChannelError) as ei:
            await assert_public_url("https://v6-internal.test")
        assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED
        assert "::1" in str(ei.value)


@pytest.mark.asyncio
async def test_ssrf_allows_public_ipv6():
    with patch(
            "socket.getaddrinfo",
            return_value=[(socket.AF_INET6, 0, 0, "", ("2606:4700:4700::1111", 0, 0, 0))],
    ):
        # Should not raise
        await assert_public_url("https://ipv6-public.example")


# ---- Full _handle_message_event pipeline drive ------------------------------


@pytest.mark.asyncio
async def test_handle_message_event_end_to_end_dispatches_to_user():
    """Feed a realistic im.message.receive_v1-shaped object all the way
    through pipeline + safety + dispatch → user handler."""
    c = _ChannelClient(app_id="cli_x", app_secret="sec")
    c._ensure_bg_loop()
    # Simulate bot identity so policy-gate's mention logic is correct
    c._bot_open_id = "ou_bot"
    c._safety.set_bot_open_id("ou_bot")

    got = []

    async def on_message(event):
        got.append(event)

    c.on("message", on_message)

    # Craft a minimal event payload (attribute-only, like the real P2 object)
    import json as _json
    now_ms = int(time.time() * 1000)
    payload = SimpleNamespace(
        header=SimpleNamespace(event_id=f"e_{now_ms}"),
        event=SimpleNamespace(
            sender=SimpleNamespace(
                sender_id=SimpleNamespace(open_id="ou_u1", user_id="u1"),
                sender_type="user",
            ),
            message=SimpleNamespace(
                message_id=f"om_{now_ms}",
                root_id="",
                parent_id="",
                create_time=str(now_ms),
                update_time=str(now_ms),
                chat_id="oc_p2p",
                thread_id=None,
                chat_type="p2p",
                message_type="text",
                content=_json.dumps({"text": "hello world"}),
                mentions=[],
                user_agent=None,
            ),
        ),
    )

    # Must run the driver on the background loop so the SafetyPipeline's
    # ChatPipeline timers get scheduled on the right loop.
    fut = asyncio.run_coroutine_threadsafe(
        c._handle_message_event(payload), c._bg_loop,
    )
    fut.result(timeout=5)
    # Give the safety pipeline's batch debounce time to fire + handler to run.
    await asyncio.sleep(1.0)
    assert len(got) == 1, f"user handler never fired; got={got}"
    assert got[0].content.text == "hello world"
    assert got[0].conversation.chat_id == "oc_p2p"


# ---- sender._gather_buffer URL path with SSRF guard ------------------------


@pytest.mark.asyncio
async def test_outbound_url_source_blocked_by_ssrf_guard_in_flight():
    """`OutboundImage(source=MediaSource(kind='url', url=<private>))` must be
    stopped by the SSRF guard before any httpx.get.

    ``gather_buffer`` raises a typed
    :class:`FeishuChannelError(SSRF_BLOCKED)` instead of silently
    returning ``(None, default)``. Silent drop made SSRF blocks
    indistinguishable from transient network failures upstream.
    """
    from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode
    from lark_oapi.channel.outbound.media.uploader import gather_buffer as _gather_buffer
    from lark_oapi.channel.types import MediaSource

    # Case 1: no allowlist configured -> hard stop.
    source = MediaSource(kind="url", url="https://internal.test/secret.png")
    with pytest.raises(FeishuChannelError) as ei:
        await _gather_buffer(source, "default.bin")
    assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED

    # Case 2: allowlist contains a DIFFERENT host than the one being
    # downloaded → fall through to assert_public_url, DNS resolves to
    # private IP → blocked. (If the allowlist matched, assert_public_url
    # would skip DNS checks because the operator explicitly trusts that
    # hostname.)
    source2 = MediaSource(kind="url", url="https://evil.test/secret.png")
    source2._ssrf_allowlist = ["not-evil.test"]  # type: ignore[attr-defined]
    with patch(
            "socket.getaddrinfo",
            return_value=[(socket.AF_INET, 0, 0, "", ("10.0.0.5", 0))],
    ):
        with pytest.raises(FeishuChannelError) as ei2:
            await _gather_buffer(source2, "default.bin")
    assert ei2.value.code == FeishuChannelErrorCode.SSRF_BLOCKED


@pytest.mark.asyncio
async def test_outbound_file_source_reads_bytes(tmp_path):
    from lark_oapi.channel.outbound.media.uploader import gather_buffer as _gather_buffer
    from lark_oapi.channel.types import MediaSource

    p = tmp_path / "foo.bin"
    p.write_bytes(b"\x00\x01\x02\x03")
    data, name = await _gather_buffer(MediaSource(kind="file", path=str(p)), "default.bin")
    assert data == b"\x00\x01\x02\x03"
    assert name == "foo.bin"


@pytest.mark.asyncio
async def test_outbound_file_source_missing_path_raises_upload_failed():
    """Updated semantics: ``gather_buffer`` now raises
    ``FeishuChannelError(UPLOAD_FAILED)`` when a local file can't be read,
    instead of silently returning ``(None, default)``. The original OSError
    is preserved via ``__cause__``. See test_upload_error_propagation.py
    for the full rationale."""
    from lark_oapi.channel.errors import (
        FeishuChannelError,
        FeishuChannelErrorCode,
    )
    from lark_oapi.channel.outbound.media.uploader import gather_buffer as _gather_buffer
    from lark_oapi.channel.types import MediaSource

    with pytest.raises(FeishuChannelError) as ei:
        await _gather_buffer(
            MediaSource(kind="file", path="/nonexistent/path/xyz.bin"),
            "default.bin",
        )
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert isinstance(ei.value.__cause__, OSError)
