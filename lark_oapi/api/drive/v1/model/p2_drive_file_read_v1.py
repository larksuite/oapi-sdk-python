# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .user_id import UserId


class P2DriveFileReadV1Data(object):
    _types = {
        "file_type": str,
        "file_token": str,
        "operator_id_list": List[UserId],
        "subscriber_id_list": List[UserId],
    }

    def __init__(self, d=None):
        self.file_type: Optional[str] = None
        self.file_token: Optional[str] = None
        self.operator_id_list: Optional[List[UserId]] = None
        self.subscriber_id_list: Optional[List[UserId]] = None
        init(self, d, self._types)


class P2DriveFileReadV1(EventContext):
    _types = {
        "event": P2DriveFileReadV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2DriveFileReadV1Data] = None
        init(self, d, self._types)