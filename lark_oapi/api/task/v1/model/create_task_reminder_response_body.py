# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .reminder import Reminder


class CreateTaskReminderResponseBody(object):
    _types = {
        "reminder": Reminder,
    }

    def __init__(self, d=None):
        self.reminder: Optional[Reminder] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateTaskReminderResponseBodyBuilder":
        return CreateTaskReminderResponseBodyBuilder()


class CreateTaskReminderResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_task_reminder_response_body = CreateTaskReminderResponseBody()

    def reminder(self, reminder: Reminder) -> "CreateTaskReminderResponseBodyBuilder":
        self._create_task_reminder_response_body.reminder = reminder
        return self

    def build(self) -> "CreateTaskReminderResponseBody":
        return self._create_task_reminder_response_body