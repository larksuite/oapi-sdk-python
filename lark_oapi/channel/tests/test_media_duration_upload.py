"""Duration-aware native audio/video upload."""

import json
import struct
from typing import Any, Dict, List

import pytest

from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import MediaSource, OutboundAudio, OutboundVideo


def _ogg_page(granule: int) -> bytes:
    header = b"OggS"
    header += bytes([0])
    header += bytes([4])
    header += struct.pack("<q", granule)
    header += struct.pack("<I", 1)
    header += struct.pack("<I", 0)
    header += struct.pack("<I", 0)
    header += bytes([0])
    return header


def _box(typ: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", 8 + len(payload)) + typ + payload


def _mp4_with_duration(*, timescale: int = 1000, duration: int = 2500) -> bytes:
    payload = bytes([0, 0, 0, 0])
    payload += struct.pack(">I", 0)
    payload += struct.pack(">I", 0)
    payload += struct.pack(">I", timescale)
    payload += struct.pack(">I", duration)
    payload += b"\x00" * 76
    return _box(b"ftyp", b"isom\x00\x00\x02\x00") + _box(b"moov", _box(b"mvhd", payload))


def _duration_driver(file_key: str = "file_duration"):
    calls: List[Dict[str, Any]] = []

    async def create_message(**kwargs):
        calls.append({"op": "create", **kwargs})
        return {
            "code": 0,
            "msg": "ok",
            "data": {"message_id": f"om_{len([c for c in calls if c['op'] == 'create'])}"},
        }

    async def upload_file(**kwargs):
        calls.append({
            "op": "upload_file",
            **{k: v for k, v in kwargs.items() if k != "data"},
        })
        return {"code": 0, "msg": "ok", "data": {"file_key": file_key}}

    return SendDriver(
        create_message=create_message,
        reply_message=create_message,
        upload_file=upload_file,
    ), calls


@pytest.mark.asyncio
async def test_audio_upload_includes_parsed_opus_duration():
    driver, calls = _duration_driver("file_audio")
    sender = OutboundSender(driver)

    result = await sender.send(
        OutboundAudio(source=MediaSource(kind="buffer", buffer=_ogg_page(48000))),
        receive_id="oc_1",
    )

    assert result.success is True
    upload = [c for c in calls if c["op"] == "upload_file"][0]
    assert upload["file_type"] == "opus"
    assert upload["duration_ms"] == 1000
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "audio"
    assert json.loads(create["content"]) == {"file_key": "file_audio"}


@pytest.mark.asyncio
async def test_video_upload_includes_parsed_mp4_duration():
    driver, calls = _duration_driver("file_video")
    sender = OutboundSender(driver)

    result = await sender.send(
        OutboundVideo(source=MediaSource(kind="buffer", buffer=_mp4_with_duration())),
        receive_id="oc_1",
    )

    assert result.success is True
    upload = [c for c in calls if c["op"] == "upload_file"][0]
    assert upload["file_type"] == "mp4"
    assert upload["duration_ms"] == 2500
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "media"
    assert json.loads(create["content"]) == {"file_key": "file_video"}


@pytest.mark.asyncio
async def test_unparseable_audio_still_uploads_without_duration():
    driver, calls = _duration_driver("file_audio")
    sender = OutboundSender(driver)

    result = await sender.send(
        OutboundAudio(source=MediaSource(kind="buffer", buffer=b"not-ogg")),
        receive_id="oc_1",
    )

    assert result.success is True
    upload = [c for c in calls if c["op"] == "upload_file"][0]
    assert upload["file_type"] == "opus"
    assert "duration_ms" not in upload


@pytest.mark.asyncio
async def test_key_source_does_not_upload_or_probe_duration():
    driver, calls = _duration_driver("should_not_upload")
    sender = OutboundSender(driver)

    result = await sender.send(
        OutboundVideo(source=MediaSource(kind="key", key="file_existing")),
        receive_id="oc_1",
    )

    assert result.success is True
    assert not [c for c in calls if c["op"] == "upload_file"]
    create = [c for c in calls if c["op"] == "create"][0]
    assert json.loads(create["content"]) == {"file_key": "file_existing"}


@pytest.mark.asyncio
async def test_legacy_upload_file_without_duration_kwarg_still_works():
    calls: List[Dict[str, Any]] = []

    async def create_message(**kwargs):
        calls.append({"op": "create", **kwargs})
        return {"code": 0, "msg": "ok", "data": {"message_id": "om_1"}}

    async def upload_file(*, data, file_name="", file_type="stream"):
        calls.append({"op": "upload_file", "file_name": file_name, "file_type": file_type})
        return {"code": 0, "msg": "ok", "data": {"file_key": "file_legacy"}}

    sender = OutboundSender(SendDriver(
        create_message=create_message,
        reply_message=create_message,
        upload_file=upload_file,
    ))

    result = await sender.send(
        OutboundAudio(source=MediaSource(kind="buffer", buffer=_ogg_page(48000))),
        receive_id="oc_1",
    )

    assert result.success is True
    upload = [c for c in calls if c["op"] == "upload_file"][0]
    assert upload == {"op": "upload_file", "file_name": "upload", "file_type": "opus"}


@pytest.mark.asyncio
async def test_url_audio_upload_includes_parsed_opus_duration(monkeypatch):
    from lark_oapi.channel.outbound.media import uploader as upload_mod

    uploads: List[Dict[str, Any]] = []

    async def fake_gather_buffer(source, default_name):
        return _ogg_page(96000), "voice.ogg"

    async def upload_file(**kwargs):
        uploads.append({k: v for k, v in kwargs.items() if k != "data"})
        return {"code": 0, "msg": "ok", "data": {"file_key": "file_audio"}}

    monkeypatch.setattr(upload_mod, "gather_buffer", fake_gather_buffer)
    driver = SendDriver(
        create_message=None,
        reply_message=None,
        upload_file=upload_file,
    )

    key = await upload_mod.resolve_media_key(
        driver,
        MediaSource(kind="url", url="https://cdn.example/voice.ogg"),
        "file",
        file_type="opus",
        duration_probe="opus",
    )

    assert key == "file_audio"
    assert uploads[0]["duration_ms"] == 2000
