# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .event_message_reader import EventMessageReader


class P2ImMessageMessageReadV1Data(object):
    _types = {
        "reader": EventMessageReader,
        "message_id_list": List[str],
    }

    def __init__(self, d=None):
        self.reader: Optional[EventMessageReader] = None
        self.message_id_list: Optional[List[str]] = None
        init(self, d, self._types)


class P2ImMessageMessageReadV1(EventContext):
    _types = {
        "event": P2ImMessageMessageReadV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2ImMessageMessageReadV1Data] = None
        init(self, d, self._types)
