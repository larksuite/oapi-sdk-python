# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class Start(object):
    _types = {
        "timestamp": int,
        "is_all_day": bool,
    }

    def __init__(self, d=None):
        self.timestamp: Optional[int] = None
        self.is_all_day: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "StartBuilder":
        return StartBuilder()


class StartBuilder(object):
    def __init__(self) -> None:
        self._start = Start()

    def timestamp(self, timestamp: int) -> "StartBuilder":
        self._start.timestamp = timestamp
        return self

    def is_all_day(self, is_all_day: bool) -> "StartBuilder":
        self._start.is_all_day = is_all_day
        return self

    def build(self) -> "Start":
        return self._start