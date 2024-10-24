# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .user_id import UserId


class P2MomentsPostCreatedV1Data(object):
    _types = {
        "id": str,
        "user_id": UserId,
        "create_time": str,
        "category_ids": List[str],
        "link": str,
        "user_type": int,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.user_id: Optional[UserId] = None
        self.create_time: Optional[str] = None
        self.category_ids: Optional[List[str]] = None
        self.link: Optional[str] = None
        self.user_type: Optional[int] = None
        init(self, d, self._types)


class P2MomentsPostCreatedV1(EventContext):
    _types = {
        "event": P2MomentsPostCreatedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2MomentsPostCreatedV1Data] = None
        init(self, d, self._types)