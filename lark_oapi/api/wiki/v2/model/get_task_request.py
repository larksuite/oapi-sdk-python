# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class GetTaskRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.task_type: Optional[str] = None
        self.task_id: Optional[str] = None

    @staticmethod
    def builder() -> "GetTaskRequestBuilder":
        return GetTaskRequestBuilder()


class GetTaskRequestBuilder(object):

    def __init__(self) -> None:
        get_task_request = GetTaskRequest()
        get_task_request.http_method = HttpMethod.GET
        get_task_request.uri = "/open-apis/wiki/v2/tasks/:task_id"
        get_task_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._get_task_request: GetTaskRequest = get_task_request

    def task_type(self, task_type: str) -> "GetTaskRequestBuilder":
        self._get_task_request.task_type = task_type
        self._get_task_request.add_query("task_type", task_type)
        return self

    def task_id(self, task_id: str) -> "GetTaskRequestBuilder":
        self._get_task_request.task_id = task_id
        self._get_task_request.paths["task_id"] = str(task_id)
        return self

    def build(self) -> GetTaskRequest:
        return self._get_task_request