# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .event_brief_info_ai import EventBriefInfoAi


class SearchEventData(object):
    _types = {
        "events": List[EventBriefInfoAi],
        "msg": str,
    }

    def __init__(self, d=None):
        self.events: Optional[List[EventBriefInfoAi]] = None
        self.msg: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchEventDataBuilder":
        return SearchEventDataBuilder()


class SearchEventDataBuilder(object):
    def __init__(self) -> None:
        self._search_event_data = SearchEventData()

    def events(self, events: List[EventBriefInfoAi]) -> "SearchEventDataBuilder":
        self._search_event_data.events = events
        return self

    def msg(self, msg: str) -> "SearchEventDataBuilder":
        self._search_event_data.msg = msg
        return self

    def build(self) -> "SearchEventData":
        return self._search_event_data
