# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class CalendarByScopeLeaveResponseBody(object):
    _types = {
        "calendar_wk_id": str,
    }

    def __init__(self, d=None):
        self.calendar_wk_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CalendarByScopeLeaveResponseBodyBuilder":
        return CalendarByScopeLeaveResponseBodyBuilder()


class CalendarByScopeLeaveResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._calendar_by_scope_leave_response_body = CalendarByScopeLeaveResponseBody()

    def calendar_wk_id(self, calendar_wk_id: str) -> "CalendarByScopeLeaveResponseBodyBuilder":
        self._calendar_by_scope_leave_response_body.calendar_wk_id = calendar_wk_id
        return self

    def build(self) -> "CalendarByScopeLeaveResponseBody":
        return self._calendar_by_scope_leave_response_body