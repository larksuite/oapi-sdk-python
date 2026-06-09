"""Regression tests for upload error propagation.

Upload failures such as server rejection, missing local files, URL download
errors, and wrong allowlists surface as typed :class:`FeishuChannelError`
instances with useful context. The sender maps those errors into
``SendResult.fail(SendError(code=e.code, ...))``.
"""

from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode
from lark_oapi.channel.outbound.media.uploader import (
    gather_buffer,
    resolve_media_key,
)
from lark_oapi.channel.outbound.sender import SendDriver
from lark_oapi.channel.types import MediaSource


# ---------------------------------------------------------------------------
# gather_buffer — typed errors instead of silent (None, default)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gather_buffer_missing_local_file_raises_upload_failed(tmp_path):
    """File doesn't exist → ``UPLOAD_FAILED`` carrying the OSError cause +
    the actual file path in the error context."""
    nonexistent = str(tmp_path / "does_not_exist.png")
    source = MediaSource(kind="file", path=nonexistent)
    with pytest.raises(FeishuChannelError) as ei:
        await gather_buffer(source, "fallback.bin")
    err = ei.value
    assert err.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert nonexistent in str(err)
    # Concrete OSError preserved via ``from e`` — callers can inspect.
    assert err.__cause__ is not None
    assert isinstance(err.__cause__, OSError)
    # Context carries diagnostics.
    assert err.context.get("path") == nonexistent
    assert err.context.get("source_kind") == "file"


@pytest.mark.asyncio
async def test_gather_buffer_url_download_network_error_raises_upload_failed(
        monkeypatch,
):
    """URL reachable per SSRF guard + allowlist, but httpx raises mid-
    download → ``UPLOAD_FAILED`` with the original exception as ``__cause__``."""
    source = MediaSource(kind="url", url="https://cdn.ok.test/a.png")
    source._ssrf_allowlist = ["cdn.ok.test"]  # type: ignore[attr-defined]

    # When the allowlist short-circuits assert_public_url, we still end up
    # inside the httpx block. Stub httpx.AsyncClient to raise.
    class _BoomClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        def stream(self, method, url):
            raise RuntimeError("simulated network blow-up")

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", _BoomClient)

    with pytest.raises(FeishuChannelError) as ei:
        await gather_buffer(source, "fallback.bin")
    err = ei.value
    assert err.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert "cdn.ok.test" in str(err)
    assert err.__cause__ is not None
    assert "simulated network blow-up" in str(err.__cause__)


@pytest.mark.asyncio
async def test_gather_buffer_url_errors_redact_sensitive_url_parts(monkeypatch):
    source = MediaSource(
        kind="url",
        url="https://user:pass@cdn.ok.test/a.png?token=secret#frag",
    )
    source._ssrf_allowlist = ["cdn.ok.test"]  # type: ignore[attr-defined]

    class _BoomClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        def stream(self, method, url):
            raise RuntimeError("simulated network blow-up")

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", _BoomClient)

    with pytest.raises(FeishuChannelError) as ei:
        await gather_buffer(source, "fallback.bin")

    rendered = str(ei.value)
    assert "cdn.ok.test" in rendered
    assert "token=secret" not in rendered
    assert "user:pass" not in rendered
    assert ei.value.context.get("url") == "https://cdn.ok.test/a.png"


# ---------------------------------------------------------------------------
# resolve_media_key — server-side upload rejection propagates code + msg
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_media_key_propagates_server_rejection_code_and_msg():
    """When the Lark backend rejects an upload with ``code=99991663`` or
    similar, the caller sees
    ``SendResult.fail(UPLOAD_FAILED, hint="... code=99991663 msg=token invalid")``
    and the context dict has raw_code/raw_msg."""
    fake_upload_image = AsyncMock(
        return_value={"code": 99991663, "msg": "invalid access_token", "data": {}}
    )
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=fake_upload_image,
        upload_file=AsyncMock(),
    )
    src = MediaSource(kind="buffer", buffer=b"\x89PNG")
    with pytest.raises(FeishuChannelError) as ei:
        await resolve_media_key(driver, src, "image")
    err = ei.value
    assert err.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert "99991663" in str(err)
    assert "invalid access_token" in str(err)
    assert err.context.get("raw_code") == 99991663
    assert err.context.get("raw_msg") == "invalid access_token"


@pytest.mark.asyncio
async def test_resolve_media_key_propagates_network_error():
    """Driver's upload coroutine raises (simulates DNS / TLS / socket
    errors). ``resolve_media_key`` wraps into UPLOAD_FAILED with the
    original exception as ``__cause__`` so tracebacks show the chain."""
    fake_upload_file = AsyncMock(side_effect=ConnectionError("DNS resolve failed"))
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=AsyncMock(),
        upload_file=fake_upload_file,
    )
    src = MediaSource(kind="buffer", buffer=b"payload")
    with pytest.raises(FeishuChannelError) as ei:
        await resolve_media_key(driver, src, "file", file_name="x.pdf")
    err = ei.value
    assert err.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert err.__cause__ is not None
    assert isinstance(err.__cause__, ConnectionError)


@pytest.mark.asyncio
async def test_resolve_media_key_flags_malformed_success_response():
    """Upload returned ``code=0`` but response has no image_key / file_key.
    Previously ``resolve_media_key`` returned None silently, so the sender
    said "empty body". Now it raises UPLOAD_FAILED so the caller can see the
    real issue (server bug / wrong endpoint / stripped proxy)."""
    fake_upload_image = AsyncMock(
        return_value={"code": 0, "msg": "", "data": {"unrelated": "value"}}
    )
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=fake_upload_image,
        upload_file=AsyncMock(),
    )
    src = MediaSource(kind="buffer", buffer=b"\x89PNG")
    with pytest.raises(FeishuChannelError) as ei:
        await resolve_media_key(driver, src, "image")
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert "missing image_key / file_key" in str(ei.value)


@pytest.mark.asyncio
async def test_resolve_media_key_missing_uploader_raises():
    """Driver has no ``upload_image`` / ``upload_file`` (mis-wired
    construction) → typed error instead of silent None."""
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=None,
        upload_file=None,
    )
    src = MediaSource(kind="buffer", buffer=b"payload")
    with pytest.raises(FeishuChannelError) as ei:
        await resolve_media_key(driver, src, "image")
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert "media uploader missing" in str(ei.value)


# ---------------------------------------------------------------------------
# End-to-end: sender.send() surfaces the typed error as SendResult.fail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_image_with_server_rejection_surfaces_upload_failed():
    """The full outbound path: ``channel.send({"image": ...})`` →
    ``OutboundSender.send`` → ``_materialize`` → ``resolve_media_key`` →
    server returns non-zero. The caller should see a ``SendResult`` with
    ``error.code == UPLOAD_FAILED`` and ``hint`` containing the raw code/msg
    — NOT the old "empty body" catch-all."""
    from lark_oapi.channel import FeishuChannel
    from lark_oapi.channel.errors import FeishuChannelErrorCode as Code

    ch = FeishuChannel(app_id="cli_x", app_secret="s")
    ch._sender._driver.upload_image = AsyncMock(  # type: ignore[attr-defined]
        return_value={
            "code": 99991663,
            "msg": "invalid access_token",
            "data": {},
        }
    )

    result = await ch.send(
        "oc_target",
        {"image": {"source": b"\x89PNG\r\n\x1a\n"}},
    )
    assert result.success is False
    assert result.error is not None
    assert result.error.code == Code.UPLOAD_FAILED
    assert "99991663" in (result.error.hint or "")
    assert "invalid access_token" in (result.error.hint or "")
    # Ensure the old catch-all is GONE.
    assert "empty body" not in (result.error.hint or "")
