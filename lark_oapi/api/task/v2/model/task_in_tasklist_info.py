# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class TaskInTasklistInfo(object):
    _types = {
        "tasklist_guid": str,
        "section_guid": str,
    }

    def __init__(self, d=None):
        self.tasklist_guid: Optional[str] = None
        self.section_guid: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TaskInTasklistInfoBuilder":
        return TaskInTasklistInfoBuilder()


class TaskInTasklistInfoBuilder(object):
    def __init__(self) -> None:
        self._task_in_tasklist_info = TaskInTasklistInfo()

    def tasklist_guid(self, tasklist_guid: str) -> "TaskInTasklistInfoBuilder":
        self._task_in_tasklist_info.tasklist_guid = tasklist_guid
        return self

    def section_guid(self, section_guid: str) -> "TaskInTasklistInfoBuilder":
        self._task_in_tasklist_info.section_guid = section_guid
        return self

    def build(self) -> "TaskInTasklistInfo":
        return self._task_in_tasklist_info