# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .event_organizer import EventOrganizer


class EventBriefInfoAi(object):
    _types = {
        "event_id": str,
        "summary": str,
        "start_time": str,
        "end_time": str,
        "app_link": str,
        "organizer": EventOrganizer,
    }

    def __init__(self, d=None):
        self.event_id: Optional[str] = None
        self.summary: Optional[str] = None
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.app_link: Optional[str] = None
        self.organizer: Optional[EventOrganizer] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "EventBriefInfoAiBuilder":
        return EventBriefInfoAiBuilder()


class EventBriefInfoAiBuilder(object):
    def __init__(self) -> None:
        self._event_brief_info_ai = EventBriefInfoAi()

    def event_id(self, event_id: str) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.event_id = event_id
        return self

    def summary(self, summary: str) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.summary = summary
        return self

    def start_time(self, start_time: str) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.start_time = start_time
        return self

    def end_time(self, end_time: str) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.end_time = end_time
        return self

    def app_link(self, app_link: str) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.app_link = app_link
        return self

    def organizer(self, organizer: EventOrganizer) -> "EventBriefInfoAiBuilder":
        self._event_brief_info_ai.organizer = organizer
        return self

    def build(self) -> "EventBriefInfoAi":
        return self._event_brief_info_ai
