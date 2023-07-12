# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init


class NotificationOption(object):
    _types = {
        "channels": List[str],
        "language": str,
    }

    def __init__(self, d):
        self.channels: Optional[List[str]] = None
        self.language: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "NotificationOptionBuilder":
        return NotificationOptionBuilder()


class NotificationOptionBuilder(object):
    def __init__(self, notification_option: NotificationOption = NotificationOption({})) -> None:
        self._notification_option: NotificationOption = notification_option
    
    def channels(self, channels: List[str]) -> "NotificationOptionBuilder":
        self._notification_option.channels = channels
        return self
    
    def language(self, language: str) -> "NotificationOptionBuilder":
        self._notification_option.language = language
        return self
    
    def build(self) -> "NotificationOption":
        return self._notification_option