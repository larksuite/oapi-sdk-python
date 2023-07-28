# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init


class TasklistSummary(object):
    _types = {
        "guid": str,
        "name": str,
    }

    def __init__(self, d=None):
        self.guid: Optional[str] = None
        self.name: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TasklistSummaryBuilder":
        return TasklistSummaryBuilder()


class TasklistSummaryBuilder(object):
    def __init__(self) -> None:
        self._tasklist_summary = TasklistSummary()

    def guid(self, guid: str) -> "TasklistSummaryBuilder":
        self._tasklist_summary.guid = guid
        return self

    def name(self, name: str) -> "TasklistSummaryBuilder":
        self._tasklist_summary.name = name
        return self

    def build(self) -> "TasklistSummary":
        return self._tasklist_summary
