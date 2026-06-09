"""Tests for the sync message-content parser."""

import json

from lark_oapi.channel.normalize.registry import SUPPORTED_MESSAGE_TYPES, parse_message_content
from lark_oapi.channel.types import (
    AudioContent,
    CalendarContent,
    FileContent,
    ImageContent,
    InteractiveContent,
    LocationContent,
    MediaContent,
    MergeForwardContent,
    PostContent,
    ShareChatContent,
    ShareUserContent,
    StickerContent,
    SystemContent,
    TextContent,
    TodoContent,
    UnknownContent,
    VideoChatContent,
    VoteContent,
)


def _c(d):
    return json.dumps(d, ensure_ascii=False)


def test_text():
    c = parse_message_content("text", _c({"text": "hello @_user_1"}))
    assert isinstance(c, TextContent)
    assert c.text == "hello @_user_1"


def test_post_flattens_text_and_title():
    post = {
        "zh_cn": {
            "title": "晴报",
            "content": [
                [{"tag": "text", "text": "hello "}, {"tag": "a", "text": "link", "href": "https://x"}],
                [{"tag": "at", "user_id": "ou_1", "user_name": "张三"}, {"tag": "text", "text": " 你好"}],
            ],
        }
    }
    c = parse_message_content("post", _c(post))
    assert isinstance(c, PostContent)
    assert c.title == "晴报"
    assert "hello link" in c.text
    assert "@张三 你好" in c.text


def test_image():
    c = parse_message_content("image", _c({"image_key": "img_xxx"}))
    assert isinstance(c, ImageContent) and c.image_key == "img_xxx"


def test_file_has_name():
    c = parse_message_content("file", _c({"file_key": "f_xxx", "file_name": "a.pdf"}))
    assert isinstance(c, FileContent)
    assert c.file_key == "f_xxx"
    assert c.file_name == "a.pdf"


def test_audio_duration():
    c = parse_message_content("audio", _c({"file_key": "a_xxx", "duration": 3200}))
    assert isinstance(c, AudioContent) and c.duration_ms == 3200


def test_media_with_cover():
    c = parse_message_content(
        "media", _c({"file_key": "v_x", "image_key": "cover_x", "duration": 5000})
    )
    assert isinstance(c, MediaContent)
    assert c.file_key == "v_x" and c.image_key == "cover_x"


def test_sticker():
    c = parse_message_content("sticker", _c({"file_key": "st"}))
    assert isinstance(c, StickerContent)


def test_interactive_v1_detect():
    c = parse_message_content("interactive", _c({"elements": [], "config": {}}))
    assert isinstance(c, InteractiveContent) and c.card_version == "v1"


def test_interactive_v2_detect():
    c = parse_message_content("interactive", _c({"schema": "2.0", "body": {"elements": []}}))
    assert isinstance(c, InteractiveContent) and c.card_version == "v2"


def test_share_chat_user_system_location():
    assert isinstance(parse_message_content("share_chat", _c({"chat_id": "oc_1"})), ShareChatContent)
    assert isinstance(parse_message_content("share_user", _c({"user_id": "ou_1"})), ShareUserContent)
    assert isinstance(parse_message_content("system", _c({"template": "add"})), SystemContent)
    loc = parse_message_content("location", _c({"name": "office", "longitude": "116.4", "latitude": "39.9"}))
    assert isinstance(loc, LocationContent)
    assert loc.longitude == 116.4 and loc.latitude == 39.9


def test_video_calendar_vote_todo():
    assert isinstance(parse_message_content("video_chat", _c({"topic": "sync"})), VideoChatContent)
    assert isinstance(parse_message_content("calendar", _c({"summary": "mtg"})), CalendarContent)
    v = parse_message_content("vote", _c({"topic": "q", "options": ["a", "b"]}))
    assert isinstance(v, VoteContent) and v.options == ["a", "b"]
    assert isinstance(parse_message_content("todo", _c({"summary": "task"})), TodoContent)


def test_merge_forward_is_loading():
    c = parse_message_content("merge_forward", _c({}))
    assert isinstance(c, MergeForwardContent) and c.loading is True


def test_unknown_fallback():
    c = parse_message_content("brand_new_type", _c({"x": 1}))
    assert isinstance(c, UnknownContent) and c.message_type == "brand_new_type"


def test_bad_json_does_not_raise():
    c = parse_message_content("text", "{{{ not json")
    assert isinstance(c, TextContent) and c.text == ""


def test_supported_covers_19_types():
    # 17 sync-parseable + interactive + merge_forward (post-merge with interactive placeholder)
    # The design doc lists 19 message formats. Check we support at least the
    # 17 types the parser handles plus interactive + merge_forward.
    assert len(SUPPORTED_MESSAGE_TYPES) == 22
    for t in (
            "text",
            "post",
            "image",
            "file",
            "audio",
            "media",
            "sticker",
            "interactive",
            "share_chat",
            "share_user",
            "system",
            "location",
            "video_chat",
            "calendar",
            "vote",
            "todo",
            "merge_forward",
    ):
        assert t in SUPPORTED_MESSAGE_TYPES
