# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class TasklistsTaskRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.task_guid: Optional[str] = None

    @staticmethod
    def builder() -> "TasklistsTaskRequestBuilder":
        return TasklistsTaskRequestBuilder()


class TasklistsTaskRequestBuilder(object):

    def __init__(self) -> None:
        tasklists_task_request = TasklistsTaskRequest()
        tasklists_task_request.http_method = HttpMethod.GET
        tasklists_task_request.uri = "/open-apis/task/v2/tasks/:task_guid/tasklists"
        tasklists_task_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._tasklists_task_request: TasklistsTaskRequest = tasklists_task_request

    def task_guid(self, task_guid: str) -> "TasklistsTaskRequestBuilder":
        self._tasklists_task_request.task_guid = task_guid
        self._tasklists_task_request.paths["task_guid"] = str(task_guid)
        return self

    def build(self) -> TasklistsTaskRequest:
        return self._tasklists_task_request