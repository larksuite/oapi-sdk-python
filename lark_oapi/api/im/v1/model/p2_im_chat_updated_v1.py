# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .chat_change import ChatChange
from .moderator_list import ModeratorList
from .user_id import UserId


class P2ImChatUpdatedV1Data(object):
    _types = {
        "chat_id": str,
        "operator_id": UserId,
        "external": bool,
        "operator_tenant_key": str,
        "after_change": ChatChange,
        "before_change": ChatChange,
        "moderator_list": ModeratorList,
    }

    def __init__(self, d=None):
        self.chat_id: Optional[str] = None
        self.operator_id: Optional[UserId] = None
        self.external: Optional[bool] = None
        self.operator_tenant_key: Optional[str] = None
        self.after_change: Optional[ChatChange] = None
        self.before_change: Optional[ChatChange] = None
        self.moderator_list: Optional[ModeratorList] = None
        init(self, d, self._types)


class P2ImChatUpdatedV1(EventContext):
    _types = {
        "event": P2ImChatUpdatedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2ImChatUpdatedV1Data] = None
        init(self, d, self._types)
