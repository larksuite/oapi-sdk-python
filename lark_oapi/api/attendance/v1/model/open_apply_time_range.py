# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .overtime_time_range import OvertimeTimeRange


class OpenApplyTimeRange(object):
    _types = {
        "overtime_attribution_date": str,
        "time_range": OvertimeTimeRange,
    }

    def __init__(self, d=None):
        self.overtime_attribution_date: Optional[str] = None
        self.time_range: Optional[OvertimeTimeRange] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "OpenApplyTimeRangeBuilder":
        return OpenApplyTimeRangeBuilder()


class OpenApplyTimeRangeBuilder(object):
    def __init__(self) -> None:
        self._open_apply_time_range = OpenApplyTimeRange()

    def overtime_attribution_date(self, overtime_attribution_date: str) -> "OpenApplyTimeRangeBuilder":
        self._open_apply_time_range.overtime_attribution_date = overtime_attribution_date
        return self

    def time_range(self, time_range: OvertimeTimeRange) -> "OpenApplyTimeRangeBuilder":
        self._open_apply_time_range.time_range = time_range
        return self

    def build(self) -> "OpenApplyTimeRange":
        return self._open_apply_time_range
