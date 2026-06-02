"""Regression tests for media serialization, upload response shape, and SSRF."""

from types import SimpleNamespace
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from lark_oapi.channel.driver import LarkClientDriver, _resp_to_dict
from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode
from lark_oapi.channel.outbound.media.uploader import (
    gather_buffer,
    resolve_media_key,
)
from lark_oapi.channel.types import MediaSource
from lark_oapi.core.json import JSON

# --------------------------------------------------------------------------- #
# JSON.marshal must not blow up on non-UTF-8 bytes (JPEG magic bytes).
# --------------------------------------------------------------------------- #


# JPEG SOI + APP0 header: 0xff 0xd8 0xff 0xe0 — classic "not valid UTF-8" blob.
_JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00"


def test_json_marshal_handles_raw_image_bytes():
    """Binary response bytes can be serialized through ``JSON.marshal``."""
    payload = {"file_key": "file_abc", "content": _JPEG_BYTES}
    out = JSON.marshal(payload)
    assert isinstance(out, str)
    import json as _json

    back = _json.loads(out)
    assert back["file_key"] == "file_abc"
    # We don't care what encoding the SDK chooses — only that it doesn't
    # crash and preserves the blob as *some* string.
    assert isinstance(back["content"], str)
    assert len(back["content"]) > 0


def test_json_marshal_nested_bytes_in_response_like_object():
    """Response-like objects containing bytes serialize without raising."""

    class _FakeResp:
        def __init__(self) -> None:
            self.code = 0
            self.msg = ""
            self.file_bytes = _JPEG_BYTES
            self.file_name = "photo.jpg"

    out = JSON.marshal(_FakeResp())
    assert isinstance(out, str)
    import json as _json

    back = _json.loads(out)
    assert back["file_name"] == "photo.jpg"
    assert isinstance(back["file_bytes"], str)


# --------------------------------------------------------------------------- #
# driver.upload_file contract — returns {"code", "msg", "data":
# {"file_key": ...}}
# --------------------------------------------------------------------------- #


def _stub_client_for_upload(file_key: Optional[str]) -> MagicMock:
    c = MagicMock()
    data = MagicMock()
    # attribute-access returns the key; _resp_to_dict round-trips via
    # JSON.marshal → vars(), so we need a real object with __dict__.
    data.__dict__ = {"file_key": file_key} if file_key is not None else {}
    resp = MagicMock()
    resp.code = 0
    resp.msg = ""
    resp.data = SimpleNamespace(file_key=file_key) if file_key is not None else None
    c.im.v1.file.acreate = AsyncMock(return_value=resp)
    c.im.v1.image.acreate = AsyncMock(return_value=resp)
    return c


@pytest.mark.asyncio
async def test_upload_file_signature_returns_file_key_shape():
    """``driver.upload_file`` returns a dict with ``data.file_key``.
    """
    c = _stub_client_for_upload(file_key="file_xyz")
    d = LarkClientDriver(c)
    raw = await d.upload_file(
        data=b"%PDF-1.4 test",
        file_name="sample.pdf",
        file_type="pdf",
    )
    assert isinstance(raw, dict)
    assert raw.get("code") == 0
    # The field downstream callers rely on.
    data = raw.get("data") or {}
    assert data.get("file_key") == "file_xyz", (
        "driver.upload_file must surface data.file_key in the dict "
        "returned to callers."
    )


@pytest.mark.asyncio
async def test_upload_file_preserves_file_key_through_resp_to_dict():
    """Direct ``_resp_to_dict`` test — guards against a regression where the
    marshaller drops ``file_key`` (e.g. filter_null or a wrong type map)."""

    # Build a response that looks like the real CreateFileResponse shape.
    class _Body:
        def __init__(self) -> None:
            self.file_key = "file_abcdef"

    resp = SimpleNamespace(code=0, msg="", data=_Body())
    out = _resp_to_dict(resp)
    assert out["code"] == 0
    assert (out.get("data") or {}).get("file_key") == "file_abcdef"


# --------------------------------------------------------------------------- #
# URL-sourced media without allowlist must surface SSRF_BLOCKED, not
# silently return None.
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_gather_buffer_url_without_allowlist_raises_ssrf_blocked():
    """URL downloads without an allowlist raise a typed SSRF_BLOCKED error.

    Returning ``None`` is indistinguishable from a transient network failure
    and can't be matched on.
    """
    src = MediaSource(kind="url", url="http://169.254.169.254/latest/meta-data/")
    with pytest.raises(FeishuChannelError) as ei:
        await gather_buffer(src, default_name="x.bin")
    assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED


@pytest.mark.asyncio
async def test_resolve_media_key_url_without_allowlist_raises():
    """End-to-end uploader path: sending an OutboundImage whose source is a
    private-IP URL should surface ``FeishuChannelError(SSRF_BLOCKED)`` to the
    caller, not quietly downgrade to ``key=None`` (which produces an empty
    message body)."""

    async def _never_called(**kwargs):  # pragma: no cover - defensive
        raise AssertionError("uploader must not be invoked for blocked URL")

    driver = SimpleNamespace(
        upload_image=_never_called,
        upload_file=_never_called,
    )
    src = MediaSource(kind="url", url="http://127.0.0.1:8080/internal.png")
    with pytest.raises(FeishuChannelError) as ei:
        await resolve_media_key(driver, src, "image")
    assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED
