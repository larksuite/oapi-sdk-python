# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class Notification(object):
    _types = {
        "idempotent_key": str,
        "content": str,
    }

    def __init__(self, d=None):
        self.idempotent_key: Optional[str] = None
        self.content: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "NotificationBuilder":
        return NotificationBuilder()


class NotificationBuilder(object):
    def __init__(self) -> None:
        self._notification = Notification()

    def idempotent_key(self, idempotent_key: str) -> "NotificationBuilder":
        self._notification.idempotent_key = idempotent_key
        return self

    def content(self, content: str) -> "NotificationBuilder":
        self._notification.content = content
        return self

    def build(self) -> "Notification":
        return self._notification
