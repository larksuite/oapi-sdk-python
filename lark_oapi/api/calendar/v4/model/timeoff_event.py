# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class TimeoffEvent(object):
    _types = {
        "timeoff_event_id": str,
        "user_id": str,
        "timezone": str,
        "start_time": str,
        "end_time": str,
        "title": str,
        "description": str,
    }

    def __init__(self, d=None):
        self.timeoff_event_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.timezone: Optional[str] = None
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TimeoffEventBuilder":
        return TimeoffEventBuilder()


class TimeoffEventBuilder(object):
    def __init__(self) -> None:
        self._timeoff_event = TimeoffEvent()

    def timeoff_event_id(self, timeoff_event_id: str) -> "TimeoffEventBuilder":
        self._timeoff_event.timeoff_event_id = timeoff_event_id
        return self

    def user_id(self, user_id: str) -> "TimeoffEventBuilder":
        self._timeoff_event.user_id = user_id
        return self

    def timezone(self, timezone: str) -> "TimeoffEventBuilder":
        self._timeoff_event.timezone = timezone
        return self

    def start_time(self, start_time: str) -> "TimeoffEventBuilder":
        self._timeoff_event.start_time = start_time
        return self

    def end_time(self, end_time: str) -> "TimeoffEventBuilder":
        self._timeoff_event.end_time = end_time
        return self

    def title(self, title: str) -> "TimeoffEventBuilder":
        self._timeoff_event.title = title
        return self

    def description(self, description: str) -> "TimeoffEventBuilder":
        self._timeoff_event.description = description
        return self

    def build(self) -> "TimeoffEvent":
        return self._timeoff_event