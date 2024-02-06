# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class Freebusy(object):
    _types = {
        "start_time": str,
        "end_time": str,
    }

    def __init__(self, d=None):
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FreebusyBuilder":
        return FreebusyBuilder()


class FreebusyBuilder(object):
    def __init__(self) -> None:
        self._freebusy = Freebusy()

    def start_time(self, start_time: str) -> "FreebusyBuilder":
        self._freebusy.start_time = start_time
        return self

    def end_time(self, end_time: str) -> "FreebusyBuilder":
        self._freebusy.end_time = end_time
        return self

    def build(self) -> "Freebusy":
        return self._freebusy