# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .instance import Instance


class InstancesCalendarEventResponseBody(object):
    _types = {
        "items": List[Instance],
        "page_token": str,
        "has_more": bool,
    }

    def __init__(self, d=None):
        self.items: Optional[List[Instance]] = None
        self.page_token: Optional[str] = None
        self.has_more: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "InstancesCalendarEventResponseBodyBuilder":
        return InstancesCalendarEventResponseBodyBuilder()


class InstancesCalendarEventResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._instances_calendar_event_response_body = InstancesCalendarEventResponseBody()

    def items(self, items: List[Instance]) -> "InstancesCalendarEventResponseBodyBuilder":
        self._instances_calendar_event_response_body.items = items
        return self

    def page_token(self, page_token: str) -> "InstancesCalendarEventResponseBodyBuilder":
        self._instances_calendar_event_response_body.page_token = page_token
        return self

    def has_more(self, has_more: bool) -> "InstancesCalendarEventResponseBodyBuilder":
        self._instances_calendar_event_response_body.has_more = has_more
        return self

    def build(self) -> "InstancesCalendarEventResponseBody":
        return self._instances_calendar_event_response_body
