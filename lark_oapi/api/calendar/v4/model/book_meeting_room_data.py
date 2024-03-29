# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .room_meta import RoomMeta


class BookMeetingRoomData(object):
    _types = {
        "meeting_room_id": str,
        "hint": str,
        "rooms": List[RoomMeta],
        "recurrence_rule": str,
    }

    def __init__(self, d=None):
        self.meeting_room_id: Optional[str] = None
        self.hint: Optional[str] = None
        self.rooms: Optional[List[RoomMeta]] = None
        self.recurrence_rule: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BookMeetingRoomDataBuilder":
        return BookMeetingRoomDataBuilder()


class BookMeetingRoomDataBuilder(object):
    def __init__(self) -> None:
        self._book_meeting_room_data = BookMeetingRoomData()

    def meeting_room_id(self, meeting_room_id: str) -> "BookMeetingRoomDataBuilder":
        self._book_meeting_room_data.meeting_room_id = meeting_room_id
        return self

    def hint(self, hint: str) -> "BookMeetingRoomDataBuilder":
        self._book_meeting_room_data.hint = hint
        return self

    def rooms(self, rooms: List[RoomMeta]) -> "BookMeetingRoomDataBuilder":
        self._book_meeting_room_data.rooms = rooms
        return self

    def recurrence_rule(self, recurrence_rule: str) -> "BookMeetingRoomDataBuilder":
        self._book_meeting_room_data.recurrence_rule = recurrence_rule
        return self

    def build(self) -> "BookMeetingRoomData":
        return self._book_meeting_room_data
