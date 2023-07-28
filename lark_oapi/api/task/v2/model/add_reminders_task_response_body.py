# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from .task import Task


class AddRemindersTaskResponseBody(object):
    _types = {
        "task": Task,
    }

    def __init__(self, d=None):
        self.task: Optional[Task] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AddRemindersTaskResponseBodyBuilder":
        return AddRemindersTaskResponseBodyBuilder()


class AddRemindersTaskResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._add_reminders_task_response_body = AddRemindersTaskResponseBody()

    def task(self, task: Task) -> "AddRemindersTaskResponseBodyBuilder":
        self._add_reminders_task_response_body.task = task
        return self

    def build(self) -> "AddRemindersTaskResponseBody":
        return self._add_reminders_task_response_body
