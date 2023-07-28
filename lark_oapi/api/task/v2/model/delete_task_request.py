# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class DeleteTaskRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.task_guid: Optional[str] = None

    @staticmethod
    def builder() -> "DeleteTaskRequestBuilder":
        return DeleteTaskRequestBuilder()


class DeleteTaskRequestBuilder(object):

    def __init__(self) -> None:
        delete_task_request = DeleteTaskRequest()
        delete_task_request.http_method = HttpMethod.DELETE
        delete_task_request.uri = "/open-apis/task/v2/tasks/:task_guid"
        delete_task_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._delete_task_request: DeleteTaskRequest = delete_task_request

    def task_guid(self, task_guid: str) -> "DeleteTaskRequestBuilder":
        self._delete_task_request.task_guid = task_guid
        self._delete_task_request.paths["task_guid"] = str(task_guid)
        return self

    def build(self) -> DeleteTaskRequest:
        return self._delete_task_request
