"""Media upload and standalone resource download response contracts.

These tests cover two contracts:

- Upload helpers pass file payloads as named ``io.IOBase`` streams so the
  multipart serializer includes the image/file part.
- Standalone image/file keys download through the standalone resource
  endpoints when no ``message_id`` is available.

SSRF blocking behavior is covered in
:mod:`test_media_upload_download_regressions` and
:mod:`test_seen_cache_and_ssrf_paths`.
"""

import io
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from lark_oapi.api.im.v1.model.create_file_response import CreateFileResponse
from lark_oapi.api.im.v1.model.create_file_response_body import CreateFileResponseBody
from lark_oapi.api.im.v1.model.create_image_response import CreateImageResponse
from lark_oapi.api.im.v1.model.create_image_response_body import CreateImageResponseBody
from lark_oapi.channel import _api_helpers
from lark_oapi.channel.driver import LarkClientDriver, _resp_to_dict
from lark_oapi.channel.outbound.media.uploader import _unwrap


# ---------------------------------------------------------------------------
# Real response objects.
# ---------------------------------------------------------------------------


def test_resp_to_dict_extracts_image_key_from_real_response():
    body = CreateImageResponseBody.builder().image_key("img_v2_real").build()
    resp = CreateImageResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = body

    out = _resp_to_dict(resp)
    assert out["code"] == 0
    assert out["data"]["image_key"] == "img_v2_real"


def test_resp_to_dict_extracts_file_key_from_real_response():
    body = CreateFileResponseBody.builder().file_key("file_v2_real").build()
    resp = CreateFileResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = body

    out = _resp_to_dict(resp)
    assert out["code"] == 0
    assert out["data"]["file_key"] == "file_v2_real"


def test_unwrap_passes_through_real_response_body():
    body = CreateImageResponseBody.builder().image_key("img_via_unwrap").build()
    resp = CreateImageResponse()
    resp.code = 0
    resp.data = body

    out = _unwrap(resp)
    assert out["data"]["image_key"] == "img_via_unwrap"


# ---------------------------------------------------------------------------
# Mock responses also preserve upload keys through fallback extraction.
# ---------------------------------------------------------------------------


def test_resp_to_dict_handles_mock_spec_body_via_dir_fallback():
    """``JSON.marshal(Mock(spec=Body))`` raises ``TypeError: cannot pickle
    'mappingproxy'``; the except branch falls back to ``dir()`` sweep and
    still surfaces the explicitly-set ``image_key``."""
    mock_body = Mock(spec=CreateImageResponseBody)
    mock_body.image_key = "img_mock_spec"

    resp = CreateImageResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = mock_body

    out = _resp_to_dict(resp)
    assert out["code"] == 0
    assert out["data"]["image_key"] == "img_mock_spec"


def test_unwrap_extracts_image_key_via_dir_from_mock_spec_body():
    """``_unwrap`` doesn't try JSON.marshal at all for non-dict data; it
    uses ``dir()`` directly, which handles mock objects natively."""
    mock_body = Mock(spec=CreateImageResponseBody)
    mock_body.image_key = "img_unwrap_mock"

    # ``_unwrap`` accepts either a typed response-like object or a dict.
    fake_response_like = Mock()
    fake_response_like.code = 0
    fake_response_like.msg = "ok"
    fake_response_like.data = mock_body

    out = _unwrap(fake_response_like)
    assert out["code"] == 0
    assert out["data"]["image_key"] == "img_unwrap_mock"


def test_unwrap_passthrough_when_driver_already_returned_dict():
    """After ``driver.upload_image`` runs its own ``_resp_to_dict``, the
    result is already a plain dict. ``_unwrap`` must pass it through
    without re-processing (else the wire contract breaks)."""
    pre_normalised = {
        "code": 0,
        "msg": "ok",
        "data": {"image_key": "img_already_dict"},
    }
    out = _unwrap(pre_normalised)
    assert out is pre_normalised  # identity, not a copy — cheap passthrough


# ---------------------------------------------------------------------------
# End-to-end: full upload pipeline through ``resolve_media_key``
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_media_key_image_end_to_end():
    """Exercise the full chain the sender walks: a driver that returns a
    realistic dict (as the real ``LarkClientDriver.upload_image`` would
    after running ``_resp_to_dict``), and assert that ``resolve_media_key``
    returns the image_key string.

    This is the regression guard for "empty body" reports: if ANY step in
    this chain drops the key, ``resolve_media_key`` returns ``None`` and
    the sender emits ``SendResult.fail(UNKNOWN, "empty body")``."""
    from lark_oapi.channel.outbound.media.uploader import resolve_media_key
    from lark_oapi.channel.outbound.sender import SendDriver
    from lark_oapi.channel.types import MediaSource
    from unittest.mock import AsyncMock

    fake_upload_image = AsyncMock(
        return_value={"code": 0, "msg": "", "data": {"image_key": "img_e2e"}}
    )
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=fake_upload_image,
        upload_file=AsyncMock(),
    )
    src = MediaSource(kind="buffer", buffer=b"\x89PNG\r\n\x1a\n...")
    key = await resolve_media_key(driver, src, "image")
    assert key == "img_e2e"
    fake_upload_image.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_media_key_file_end_to_end():
    from lark_oapi.channel.outbound.media.uploader import resolve_media_key
    from lark_oapi.channel.outbound.sender import SendDriver
    from lark_oapi.channel.types import MediaSource
    from unittest.mock import AsyncMock

    fake_upload_file = AsyncMock(
        return_value={"code": 0, "msg": "", "data": {"file_key": "file_e2e"}}
    )
    driver = SendDriver(
        create_message=AsyncMock(),
        reply_message=AsyncMock(),
        upload_image=AsyncMock(),
        upload_file=fake_upload_file,
    )
    src = MediaSource(kind="buffer", buffer=b"%PDF-1.7...")
    key = await resolve_media_key(driver, src, "file", file_name="sample.pdf")
    assert key == "file_e2e"


@pytest.mark.asyncio
async def test_upload_image_via_real_driver_response_shape():
    """Full loop: driver.upload_image's actual internal pipeline uses
    ``_resp_to_dict`` on a real ``CreateImageResponse``. Here we mock only
    ``self._client.im.v1.image.acreate`` and let the rest run for real, so
    any regression in ``_resp_to_dict`` would surface here — NOT in a
    separately-crafted dict fixture.
    """
    body = CreateImageResponseBody.builder().image_key("img_driver_e2e").build()
    resp = CreateImageResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = body

    client = MagicMock()
    client.im.v1.image.acreate = AsyncMock(return_value=resp)

    driver = LarkClientDriver(client)
    out = await driver.upload_image(data=b"\x89PNG\r\n", file_name="x.png")
    assert out["code"] == 0
    assert out["data"]["image_key"] == "img_driver_e2e"


# ---------------------------------------------------------------------------
# Real root cause 1: upload must pass an IO stream, not raw bytes.
# ---------------------------------------------------------------------------


def _captured_image_body(client_mock: MagicMock) -> object:
    """Pull the `request_body` off the ``CreateImageRequest`` the driver
    handed to ``image.acreate``. A single ``.call_args`` assertion would
    be fragile (SDK may wrap in RequestOption), so we match by object
    type instead."""
    from lark_oapi.api.im.v1.model.create_image_request import CreateImageRequest

    call_args = client_mock.im.v1.image.acreate.call_args
    req = next(a for a in call_args.args if isinstance(a, CreateImageRequest))
    return req.request_body


def _captured_file_body(client_mock: MagicMock) -> object:
    from lark_oapi.api.im.v1.model.create_file_request import CreateFileRequest

    call_args = client_mock.im.v1.file.acreate.call_args
    req = next(a for a in call_args.args if isinstance(a, CreateFileRequest))
    return req.request_body


@pytest.mark.asyncio
async def test_upload_image_passes_iobase_stream_not_bytes():
    """``Files.extract_files`` only picks up fields
    that are ``io.IOBase`` instances. If the driver passes raw ``bytes``,
    the multipart part is silently dropped and the server returns
    ``234001 Invalid request param``.

    This test mocks the low-level client and asserts the ``image`` field on
    the outgoing request body is an ``IOBase`` carrying the original bytes
    and a filename — which is what the Feishu API actually needs to accept
    the upload."""
    resp = CreateImageResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = CreateImageResponseBody.builder().image_key("img_ok").build()

    client = MagicMock()
    client.im.v1.image.acreate = AsyncMock(return_value=resp)

    driver = LarkClientDriver(client)
    payload = b"\x89PNG\r\n\x1a\nbody-bytes"
    await driver.upload_image(data=payload, file_name="sample.png")

    body = _captured_image_body(client)
    assert body.image_type == "message"
    assert isinstance(body.image, io.IOBase), (
        f"driver must pass io.IOBase (SDK's Files.extract_files filter); "
        f"got {type(body.image).__name__}"
    )
    # filename is required for the multipart Content-Disposition
    assert getattr(body.image, "name", "") == "sample.png"
    # and the IO must yield the original payload when read
    body.image.seek(0)
    assert body.image.read() == payload


@pytest.mark.asyncio
async def test_upload_file_passes_iobase_stream_not_bytes():
    """Same IOBase requirement, on the file endpoint. Also pin that the
    file_name is plumbed through both the dedicated ``file_name`` field AND
    the IO stream's ``.name`` (the SDK looks at both in different code
    paths)."""
    from lark_oapi.api.im.v1.model.create_file_response_body import CreateFileResponseBody as _Body
    resp = CreateFileResponse()
    resp.code = 0
    resp.msg = "ok"
    resp.data = _Body.builder().file_key("file_ok").build()

    client = MagicMock()
    client.im.v1.file.acreate = AsyncMock(return_value=resp)

    driver = LarkClientDriver(client)
    payload = b"%PDF-1.7\nbinary-ish\x00\xff"
    await driver.upload_file(
        data=payload, file_name="doc.pdf", file_type="pdf"
    )

    body = _captured_file_body(client)
    assert body.file_type == "pdf"
    assert body.file_name == "doc.pdf"
    assert isinstance(body.file, io.IOBase)
    assert getattr(body.file, "name", "") == "doc.pdf"
    body.file.seek(0)
    assert body.file.read() == payload


@pytest.mark.asyncio
async def test_upload_file_uses_default_name_when_caller_omits_it():
    """Don't break existing callers that don't pass file_name — the stream
    still needs *some* ``.name`` so the multipart Content-Disposition is
    valid."""
    resp = CreateFileResponse()
    resp.code = 0
    resp.data = CreateFileResponseBody.builder().file_key("file_noname").build()

    client = MagicMock()
    client.im.v1.file.acreate = AsyncMock(return_value=resp)

    driver = LarkClientDriver(client)
    await driver.upload_file(data=b"bytes")

    body = _captured_file_body(client)
    assert body.file_name  # some non-empty default
    assert getattr(body.file, "name", "") == body.file_name


# ---------------------------------------------------------------------------
# Real root cause 2: download_media must route by presence of message_id.
# ---------------------------------------------------------------------------


class _FakeFile:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


@pytest.mark.asyncio
async def test_download_image_without_message_id_uses_image_get():
    """Standalone image key (uploaded via ``image.create`` then downloaded
    by key only): must hit ``GET /im/v1/images/:image_key``, not the
    ``/messages/:id/resources/:file_key`` endpoint. The latter returned an
    empty body when the caller had no message_id."""
    resp = MagicMock()
    resp.code = 0
    resp.file = _FakeFile(b"\x89PNG-bytes")

    client = MagicMock()
    client.im.v1.image.aget = AsyncMock(return_value=resp)
    client.im.v1.file.aget = AsyncMock(side_effect=AssertionError("wrong endpoint"))
    client.im.v1.message_resource.aget = AsyncMock(
        side_effect=AssertionError("wrong endpoint")
    )

    out = await _api_helpers.download_media(
        client, message_id="", file_key="img_standalone", resource_type="image"
    )
    assert out == b"\x89PNG-bytes"
    client.im.v1.image.aget.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_file_without_message_id_uses_file_get():
    resp = MagicMock()
    resp.code = 0
    resp.file = _FakeFile(b"%PDF-bytes")

    client = MagicMock()
    client.im.v1.file.aget = AsyncMock(return_value=resp)
    client.im.v1.image.aget = AsyncMock(side_effect=AssertionError("wrong endpoint"))
    client.im.v1.message_resource.aget = AsyncMock(
        side_effect=AssertionError("wrong endpoint")
    )

    out = await _api_helpers.download_media(
        client, message_id="", file_key="file_standalone", resource_type="file"
    )
    assert out == b"%PDF-bytes"
    client.im.v1.file.aget.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_media_with_message_id_still_uses_message_resource():
    """Don't regress the message-attachment path: when a message_id IS
    supplied, the key belongs to a message and must be fetched via
    ``message_resource.aget`` so the server can authorize it against the
    conversation."""
    resp = MagicMock()
    resp.code = 0
    resp.file = _FakeFile(b"attachment-bytes")

    client = MagicMock()
    client.im.v1.message_resource.aget = AsyncMock(return_value=resp)
    client.im.v1.image.aget = AsyncMock(side_effect=AssertionError("wrong endpoint"))
    client.im.v1.file.aget = AsyncMock(side_effect=AssertionError("wrong endpoint"))

    out = await _api_helpers.download_media(
        client,
        message_id="om_xxx",
        file_key="file_in_msg",
        resource_type="file",
    )
    assert out == b"attachment-bytes"
    client.im.v1.message_resource.aget.assert_awaited_once()
