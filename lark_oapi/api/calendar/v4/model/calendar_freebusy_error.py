# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class CalendarFreebusyError(object):
    _types = {
        "calendar_id": str,
        "error_msg": str,
    }

    def __init__(self, d=None):
        self.calendar_id: Optional[str] = None
        self.error_msg: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CalendarFreebusyErrorBuilder":
        return CalendarFreebusyErrorBuilder()


class CalendarFreebusyErrorBuilder(object):
    def __init__(self) -> None:
        self._calendar_freebusy_error = CalendarFreebusyError()

    def calendar_id(self, calendar_id: str) -> "CalendarFreebusyErrorBuilder":
        self._calendar_freebusy_error.calendar_id = calendar_id
        return self

    def error_msg(self, error_msg: str) -> "CalendarFreebusyErrorBuilder":
        self._calendar_freebusy_error.error_msg = error_msg
        return self

    def build(self) -> "CalendarFreebusyError":
        return self._calendar_freebusy_error