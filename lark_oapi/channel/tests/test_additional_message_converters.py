"""Parser tests for additional msg_type converters."""

import json

from lark_oapi.channel.normalize.registry import parse_message_content
from lark_oapi.channel.types import (
    FolderContent,
    GeneralCalendarContent,
    HongbaoContent,
    MediaContent,
    ShareCalendarEventContent,
)


def _c(d):
    return json.dumps(d, ensure_ascii=False)


def test_folder_parsed():
    c = parse_message_content("folder", _c({"file_name": "archive", "file_size": 1024}))
    assert isinstance(c, FolderContent)
    assert c.file_name == "archive"
    assert c.file_size == 1024


def test_hongbao_parsed():
    c = parse_message_content("hongbao", _c({"text": "恭喜发财", "amount": "888"}))
    assert isinstance(c, HongbaoContent)
    assert c.text == "恭喜发财"
    assert c.amount == 888


def test_general_calendar_parsed():
    c = parse_message_content(
        "general_calendar",
        _c({"summary": "Q3 Review", "start_time": 1700000000, "end_time": 1700003600}),
    )
    assert isinstance(c, GeneralCalendarContent)
    assert c.summary == "Q3 Review"
    assert c.start_time == 1700000000


def test_share_calendar_event_parsed():
    c = parse_message_content(
        "share_calendar_event",
        _c({"summary": "Demo", "organizer_display_name": "Alice"}),
    )
    assert isinstance(c, ShareCalendarEventContent)
    assert c.summary == "Demo"
    assert c.organizer == "Alice"


def test_video_aliased_to_media():
    c = parse_message_content("video", _c({"file_key": "v_x", "duration": 5000}))
    assert isinstance(c, MediaContent)
    assert c.file_key == "v_x"
