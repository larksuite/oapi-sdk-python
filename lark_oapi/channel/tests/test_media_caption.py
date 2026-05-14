"""Image/file caption tests."""

import json
from typing import Any, Dict, List

import pytest

from lark_oapi.channel._coerce import coerce_outbound
from lark_oapi.channel.config import MarkdownConverter, OutboundConfig
from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import (
    MediaSource,
    OutboundAudio,
    OutboundFile,
    OutboundImage,
    OutboundVideo,
)


def test_coerce_image_caption():
    out = coerce_outbound({"image": {"source": "img_key"}, "caption": "hello"})
    assert isinstance(out, OutboundImage)
    assert out.caption == "hello"


def test_coerce_file_caption():
    out = coerce_outbound({"file": {"source": b"abc", "fileName": "a.txt"}, "caption": "file cap"})
    assert isinstance(out, OutboundFile)
    assert out.caption == "file cap"
    assert out.file_name == "a.txt"


def test_coerce_empty_caption_as_none():
    out = coerce_outbound({"image": {"source": "img_key"}, "caption": ""})
    assert isinstance(out, OutboundImage)
    assert out.caption is None


def test_coerce_non_string_caption_rejected():
    with pytest.raises(TypeError, match="caption must be a string"):
        coerce_outbound({"image": {"source": "img_key"}, "caption": 123})


def test_coerce_audio_video_caption():
    audio = coerce_outbound({"audio": {"source": b"audio"}, "caption": "audio cap"})
    video = coerce_outbound({"video": {"source": b"video"}, "caption": "video cap"})
    assert isinstance(audio, OutboundAudio)
    assert isinstance(video, OutboundVideo)
    assert audio.caption == "audio cap"
    assert video.caption == "video cap"


def make_caption_driver(image_key="img_x", file_key="file_x"):
    calls: List[Dict[str, Any]] = []

    async def create_message(**kwargs):
        calls.append({"op": "create", **kwargs})
        return {"code": 0, "msg": "ok", "data": {"message_id": "om_new"}}

    async def upload_image(**kwargs):
        calls.append({"op": "upload_image", **{k: v for k, v in kwargs.items() if k != "data"}})
        return {"code": 0, "data": {"image_key": image_key}}

    async def upload_file(**kwargs):
        calls.append({"op": "upload_file", **{k: v for k, v in kwargs.items() if k != "data"}})
        return {"code": 0, "data": {"file_key": file_key}}

    return SendDriver(
        create_message=create_message,
        reply_message=create_message,
        upload_image=upload_image,
        upload_file=upload_file,
    ), calls


@pytest.mark.asyncio
async def test_image_without_caption_wire_unchanged():
    d, calls = make_caption_driver(image_key="img_no_cap")
    s = OutboundSender(d)
    await s.send(
        OutboundImage(source=MediaSource(kind="buffer", buffer=b"png")),
        receive_id="oc_1",
    )
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "image"
    assert json.loads(create["content"]) == {"image_key": "img_no_cap"}


@pytest.mark.asyncio
async def test_file_without_caption_wire_unchanged():
    d, calls = make_caption_driver(file_key="file_no_cap")
    s = OutboundSender(d)
    await s.send(
        OutboundFile(source=MediaSource(kind="buffer", buffer=b"abc"), file_name="a.txt"),
        receive_id="oc_1",
    )
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "file"
    assert json.loads(create["content"]) == {"file_key": "file_no_cap"}


@pytest.mark.asyncio
async def test_image_caption_native_post_body():
    d, calls = make_caption_driver(image_key="img_cap")
    cfg = OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native"))
    s = OutboundSender(d, cfg)
    await s.send(
        OutboundImage(source=MediaSource(kind="buffer", buffer=b"png"), caption="**caption**"),
        receive_id="oc_1",
    )
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "post"
    post = json.loads(create["content"])
    assert post["zh_cn"]["content"] == [
        [{"tag": "md", "text": "**caption**"}],
        [{"tag": "img", "image_key": "img_cap"}],
    ]


@pytest.mark.asyncio
async def test_file_caption_is_rejected_without_uploading_or_sending():
    d, calls = make_caption_driver(file_key="file_cap")
    cfg = OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native"))
    s = OutboundSender(d, cfg)
    result = await s.send(
        OutboundFile(
            source=MediaSource(kind="buffer", buffer=b"abc"),
            file_name="a.txt",
            caption="file caption",
        ),
        receive_id="oc_1",
    )
    assert result.success is False
    assert result.error is not None
    assert result.error.code.value == "format_error"
    assert "file caption" in (result.error.hint or "")
    assert calls == []


@pytest.mark.asyncio
async def test_audio_caption_is_rejected_without_uploading_or_sending():
    d, calls = make_caption_driver(file_key="audio_cap")
    cfg = OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native"))
    s = OutboundSender(d, cfg)
    result = await s.send(
        OutboundAudio(
            source=MediaSource(kind="buffer", buffer=b"abc"),
            caption="audio caption",
        ),
        receive_id="oc_1",
    )
    assert result.success is False
    assert result.error is not None
    assert result.error.code.value == "format_error"
    assert "audio caption" in (result.error.hint or "")
    assert calls == []


@pytest.mark.asyncio
async def test_video_caption_native_post_body_uses_media_tag():
    d, calls = make_caption_driver(file_key="video_cap")
    cfg = OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native"))
    s = OutboundSender(d, cfg)
    await s.send(
        OutboundVideo(
            source=MediaSource(kind="buffer", buffer=b"abc"),
            caption="video caption",
        ),
        receive_id="oc_1",
    )
    create = [c for c in calls if c["op"] == "create"][0]
    assert create["msg_type"] == "post"
    post = json.loads(create["content"])
    assert post["zh_cn"]["content"] == [
        [{"tag": "md", "text": "video caption"}],
        [{"tag": "media", "file_key": "video_cap"}],
    ]


@pytest.mark.asyncio
async def test_image_caption_structured_adds_media_as_final_row():
    d, calls = make_caption_driver(image_key="img_structured")
    s = OutboundSender(d)
    await s.send(
        OutboundImage(source=MediaSource(kind="buffer", buffer=b"png"), caption="**bold**"),
        receive_id="oc_1",
    )
    create = [c for c in calls if c["op"] == "create"][0]
    post = json.loads(create["content"])
    rows = post["zh_cn"]["content"]
    assert rows[-1] == [{"tag": "img", "image_key": "img_structured"}]
    assert rows[0][0]["tag"] == "text"
    assert rows[0][0]["text"] == "bold"
