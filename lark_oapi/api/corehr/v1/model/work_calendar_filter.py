# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .wk_option import WkOption


class WorkCalendarFilter(object):
    _types = {
        "wk_calendar_ids": List[str],
        "wk_calendar_id_gt": str,
        "wk_option": WkOption,
        "only_enable": bool,
    }

    def __init__(self, d=None):
        self.wk_calendar_ids: Optional[List[str]] = None
        self.wk_calendar_id_gt: Optional[str] = None
        self.wk_option: Optional[WkOption] = None
        self.only_enable: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "WorkCalendarFilterBuilder":
        return WorkCalendarFilterBuilder()


class WorkCalendarFilterBuilder(object):
    def __init__(self) -> None:
        self._work_calendar_filter = WorkCalendarFilter()

    def wk_calendar_ids(self, wk_calendar_ids: List[str]) -> "WorkCalendarFilterBuilder":
        self._work_calendar_filter.wk_calendar_ids = wk_calendar_ids
        return self

    def wk_calendar_id_gt(self, wk_calendar_id_gt: str) -> "WorkCalendarFilterBuilder":
        self._work_calendar_filter.wk_calendar_id_gt = wk_calendar_id_gt
        return self

    def wk_option(self, wk_option: WkOption) -> "WorkCalendarFilterBuilder":
        self._work_calendar_filter.wk_option = wk_option
        return self

    def only_enable(self, only_enable: bool) -> "WorkCalendarFilterBuilder":
        self._work_calendar_filter.only_enable = only_enable
        return self

    def build(self) -> "WorkCalendarFilter":
        return self._work_calendar_filter
