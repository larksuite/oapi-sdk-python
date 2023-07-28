# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .room_event import RoomEvent


class P2VcRoomDeletedV1Data(object):
    _types = {
        "room": RoomEvent,
    }

    def __init__(self, d=None):
        self.room: Optional[RoomEvent] = None
        init(self, d, self._types)


class P2VcRoomDeletedV1(EventContext):
    _types = {
        "event": P2VcRoomDeletedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2VcRoomDeletedV1Data] = None
        init(self, d, self._types)
