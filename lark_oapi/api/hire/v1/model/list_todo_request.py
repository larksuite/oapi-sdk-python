# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListTodoRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None
        self.user_id: Optional[str] = None
        self.user_id_type: Optional[str] = None
        self.type: Optional[str] = None

    @staticmethod
    def builder() -> "ListTodoRequestBuilder":
        return ListTodoRequestBuilder()


class ListTodoRequestBuilder(object):

    def __init__(self) -> None:
        list_todo_request = ListTodoRequest()
        list_todo_request.http_method = HttpMethod.GET
        list_todo_request.uri = "/open-apis/hire/v1/todos"
        list_todo_request.token_types = {AccessTokenType.USER}
        self._list_todo_request: ListTodoRequest = list_todo_request

    def page_token(self, page_token: str) -> "ListTodoRequestBuilder":
        self._list_todo_request.page_token = page_token
        self._list_todo_request.add_query("page_token", page_token)
        return self

    def page_size(self, page_size: int) -> "ListTodoRequestBuilder":
        self._list_todo_request.page_size = page_size
        self._list_todo_request.add_query("page_size", page_size)
        return self

    def user_id(self, user_id: str) -> "ListTodoRequestBuilder":
        self._list_todo_request.user_id = user_id
        self._list_todo_request.add_query("user_id", user_id)
        return self

    def user_id_type(self, user_id_type: str) -> "ListTodoRequestBuilder":
        self._list_todo_request.user_id_type = user_id_type
        self._list_todo_request.add_query("user_id_type", user_id_type)
        return self

    def type(self, type: str) -> "ListTodoRequestBuilder":
        self._list_todo_request.type = type
        self._list_todo_request.add_query("type", type)
        return self

    def build(self) -> ListTodoRequest:
        return self._list_todo_request
