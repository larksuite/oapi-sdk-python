# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class ListTaskRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.completed: Optional[bool] = None
        self.type: Optional[str] = None
        self.user_id_type: Optional[str] = None

    @staticmethod
    def builder() -> "ListTaskRequestBuilder":
        return ListTaskRequestBuilder()


class ListTaskRequestBuilder(object):

    def __init__(self) -> None:
        list_task_request = ListTaskRequest()
        list_task_request.http_method = HttpMethod.GET
        list_task_request.uri = "/open-apis/task/v2/tasks"
        list_task_request.token_types = {AccessTokenType.USER}
        self._list_task_request: ListTaskRequest = list_task_request

    def page_size(self, page_size: int) -> "ListTaskRequestBuilder":
        self._list_task_request.page_size = page_size
        self._list_task_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListTaskRequestBuilder":
        self._list_task_request.page_token = page_token
        self._list_task_request.add_query("page_token", page_token)
        return self

    def completed(self, completed: bool) -> "ListTaskRequestBuilder":
        self._list_task_request.completed = completed
        self._list_task_request.add_query("completed", completed)
        return self

    def type(self, type: str) -> "ListTaskRequestBuilder":
        self._list_task_request.type = type
        self._list_task_request.add_query("type", type)
        return self

    def user_id_type(self, user_id_type: str) -> "ListTaskRequestBuilder":
        self._list_task_request.user_id_type = user_id_type
        self._list_task_request.add_query("user_id_type", user_id_type)
        return self

    def build(self) -> ListTaskRequest:
        return self._list_task_request
