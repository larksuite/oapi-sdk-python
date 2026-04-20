"""Tests for ``FeishuChannel.upload_media`` — public single-shot uploader.

The method wraps the internal ``resolve_media_key`` helper with a narrow,
type-disciplined surface so consumers can obtain a Feishu ``image_key`` /
``file_key`` without reaching into ``_sender._driver`` or importing from
``lark_oapi.channel.outbound.media.uploader``.

Contract (B'):
    - ``source`` must be a :class:`MediaSource` (no str / bytes coercion)
    - ``kind`` must be ``"image"`` or ``"file"`` (audio/video → ``kind="file"``
      with ``file_type="opus"`` / ``"mp4"``)
    - Returns ``str`` on success
    - Failures raise :class:`FeishuChannelError` (no None fall-through)
    - SSRF allowlist auto-pulled from ``OutboundConfig.ssrf_allowlist``
"""

from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode
from lark_oapi.channel.types import MediaSource


def _make_channel(*, ssrf_allowlist=None) -> FeishuChannel:
    """Channel with deterministic upload mocks; no network."""
    from lark_oapi.channel.config import ChannelConfig, OutboundConfig

    cfg = ChannelConfig(
        app_id="cli_test",
        app_secret="s",
        outbound=OutboundConfig(ssrf_allowlist=ssrf_allowlist),
    )
    ch = FeishuChannel(config=cfg)
    return ch


# ---------------------------------------------------------------------------
# Happy path: each MediaSource kind → corresponding driver call
# ---------------------------------------------------------------------------


async def test_upload_media_buffer_image_returns_image_key():
    ch = _make_channel()
    ch._sender._driver.upload_image = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"image_key": "img_abc"}}
    )

    key = await ch.upload_media(
        MediaSource(kind="buffer", buffer=b"\x89PNG\r\n"),
        kind="image",
    )

    assert key == "img_abc"
    ch._sender._driver.upload_image.assert_awaited_once()


async def test_upload_media_file_returns_file_key(tmp_path):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 ...")
    ch = _make_channel()
    ch._sender._driver.upload_file = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"file_key": "file_xyz"}}
    )

    key = await ch.upload_media(
        MediaSource(kind="file", path=str(pdf)),
        kind="file",
        file_name="report.pdf",
    )

    assert key == "file_xyz"
    call_kwargs = ch._sender._driver.upload_file.await_args.kwargs
    assert call_kwargs["file_name"] == "report.pdf"
    assert call_kwargs["data"] == b"%PDF-1.4 ..."


async def test_upload_media_key_passthrough_does_not_upload():
    ch = _make_channel()
    ch._sender._driver.upload_image = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"image_key": "should_not_be_used"}}
    )

    key = await ch.upload_media(
        MediaSource(kind="key", key="img_already_uploaded"),
        kind="image",
    )

    assert key == "img_already_uploaded"
    ch._sender._driver.upload_image.assert_not_awaited()


async def test_upload_media_audio_threads_file_type_opus(tmp_path):
    """audio is just 'file' kind with file_type='opus' — caller-decided."""
    audio = tmp_path / "voice.opus"
    audio.write_bytes(b"OggS\x00\x02")
    ch = _make_channel()
    ch._sender._driver.upload_file = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"file_key": "file_audio"}}
    )

    key = await ch.upload_media(
        MediaSource(kind="file", path=str(audio)),
        kind="file",
        file_type="opus",
    )

    assert key == "file_audio"
    assert ch._sender._driver.upload_file.await_args.kwargs["file_type"] == "opus"


async def test_upload_media_video_threads_file_type_mp4(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    ch = _make_channel()
    ch._sender._driver.upload_file = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"file_key": "file_video"}}
    )

    key = await ch.upload_media(
        MediaSource(kind="file", path=str(video)),
        kind="file",
        file_type="mp4",
    )

    assert key == "file_video"
    assert ch._sender._driver.upload_file.await_args.kwargs["file_type"] == "mp4"


# ---------------------------------------------------------------------------
# Error semantics: raise FeishuChannelError, never return None
# ---------------------------------------------------------------------------


async def test_upload_media_server_rejection_raises_upload_failed():
    ch = _make_channel()
    ch._sender._driver.upload_image = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 99991663, "msg": "invalid access_token", "data": {}}
    )

    with pytest.raises(FeishuChannelError) as ei:
        await ch.upload_media(
            MediaSource(kind="buffer", buffer=b"\x89PNG"),
            kind="image",
        )
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED
    assert "99991663" in str(ei.value)


async def test_upload_media_missing_local_file_raises_upload_failed(tmp_path):
    ch = _make_channel()
    nonexistent = tmp_path / "nope.png"

    with pytest.raises(FeishuChannelError) as ei:
        await ch.upload_media(
            MediaSource(kind="file", path=str(nonexistent)),
            kind="image",
        )
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED


async def test_upload_media_url_without_allowlist_raises_ssrf_blocked():
    ch = _make_channel(ssrf_allowlist=None)

    with pytest.raises(FeishuChannelError) as ei:
        await ch.upload_media(
            MediaSource(kind="url", url="https://attacker.example/x.png"),
            kind="image",
        )
    assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED


async def test_upload_media_empty_key_raises_upload_failed():
    """``MediaSource(kind="key", key="")`` has no uploadable content; the
    underlying helper returns None for this — the public method must convert
    that to an explicit ``UPLOAD_FAILED`` so callers don't see ``Optional[str]``.
    """
    ch = _make_channel()

    with pytest.raises(FeishuChannelError) as ei:
        await ch.upload_media(
            MediaSource(kind="key", key=""),
            kind="image",
        )
    assert ei.value.code == FeishuChannelErrorCode.UPLOAD_FAILED


# ---------------------------------------------------------------------------
# Type discipline: reject str / bytes / wrong kind
# ---------------------------------------------------------------------------


async def test_upload_media_rejects_str_source():
    ch = _make_channel()
    with pytest.raises(TypeError, match="MediaSource"):
        await ch.upload_media("/tmp/x.png", kind="image")  # type: ignore[arg-type]


async def test_upload_media_rejects_bytes_source():
    ch = _make_channel()
    with pytest.raises(TypeError, match="MediaSource"):
        await ch.upload_media(b"\x89PNG", kind="image")  # type: ignore[arg-type]


async def test_upload_media_rejects_unknown_kind():
    ch = _make_channel()
    with pytest.raises(ValueError, match="kind"):
        await ch.upload_media(
            MediaSource(kind="buffer", buffer=b"x"),
            kind="audio",  # type: ignore[arg-type]  # B' rejects audio/video as kind
        )


# ---------------------------------------------------------------------------
# SSRF allowlist auto-threaded from OutboundConfig
# ---------------------------------------------------------------------------


async def test_upload_media_url_uses_outbound_config_allowlist(monkeypatch):
    """``OutboundConfig.ssrf_allowlist`` flows through transparently — caller
    does NOT need to set ``source._ssrf_allowlist`` manually."""
    ch = _make_channel(ssrf_allowlist=["cdn.ok.test"])
    ch._sender._driver.upload_image = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "msg": "", "data": {"image_key": "img_url"}}
    )

    # Stub assert_public_url to a no-op so we don't actually resolve DNS.
    async def _noop(url, *, allowlist):
        # The allowlist must be the outbound config's value (not None).
        assert allowlist == ["cdn.ok.test"]

    from lark_oapi.channel.outbound.media import uploader as _uploader_mod

    monkeypatch.setattr(_uploader_mod, "assert_public_url", _noop)

    # Stub httpx.AsyncClient to return a tiny payload.
    class _FakeResp:
        headers = {"content-length": "4"}

        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b"data"

    class _FakeStream:
        def __init__(self, resp):
            self._resp = resp

        async def __aenter__(self):
            return self._resp

        async def __aexit__(self, *a):
            return False

    class _FakeClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        def stream(self, method, url):
            return _FakeStream(_FakeResp())

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)

    key = await ch.upload_media(
        MediaSource(kind="url", url="https://cdn.ok.test/x.png"),
        kind="image",
    )

    assert key == "img_url"
