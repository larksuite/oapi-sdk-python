# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .task import Task


class ListTaskSubtaskResponseBody(object):
    _types = {
        "items": List[Task],
        "page_token": str,
        "has_more": bool,
    }

    def __init__(self, d=None):
        self.items: Optional[List[Task]] = None
        self.page_token: Optional[str] = None
        self.has_more: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ListTaskSubtaskResponseBodyBuilder":
        return ListTaskSubtaskResponseBodyBuilder()


class ListTaskSubtaskResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._list_task_subtask_response_body = ListTaskSubtaskResponseBody()

    def items(self, items: List[Task]) -> "ListTaskSubtaskResponseBodyBuilder":
        self._list_task_subtask_response_body.items = items
        return self

    def page_token(self, page_token: str) -> "ListTaskSubtaskResponseBodyBuilder":
        self._list_task_subtask_response_body.page_token = page_token
        return self

    def has_more(self, has_more: bool) -> "ListTaskSubtaskResponseBodyBuilder":
        self._list_task_subtask_response_body.has_more = has_more
        return self

    def build(self) -> "ListTaskSubtaskResponseBody":
        return self._list_task_subtask_response_body