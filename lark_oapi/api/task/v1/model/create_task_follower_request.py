# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .follower import Follower


class CreateTaskFollowerRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.task_id: Optional[str] = None
        self.request_body: Optional[Follower] = None

    @staticmethod
    def builder() -> "CreateTaskFollowerRequestBuilder":
        return CreateTaskFollowerRequestBuilder()


class CreateTaskFollowerRequestBuilder(object):

    def __init__(self, create_task_follower_request: CreateTaskFollowerRequest = CreateTaskFollowerRequest()) -> None:
        create_task_follower_request.http_method = HttpMethod.POST
        create_task_follower_request.uri = "/open-apis/task/v1/tasks/:task_id/followers"
        create_task_follower_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._create_task_follower_request: CreateTaskFollowerRequest = create_task_follower_request
    
    def user_id_type(self, user_id_type: str) -> "CreateTaskFollowerRequestBuilder":
        self._create_task_follower_request.user_id_type = user_id_type
        self._create_task_follower_request.queries["user_id_type"] = str(user_id_type)
        return self
    
    def task_id(self, task_id: str) -> "CreateTaskFollowerRequestBuilder":
        self._create_task_follower_request.task_id = task_id
        self._create_task_follower_request.paths["task_id"] = task_id
        return self
    
    def request_body(self, request_body: Follower) -> "CreateTaskFollowerRequestBuilder":
        self._create_task_follower_request.request_body = request_body
        self._create_task_follower_request.body = request_body
        return self

    def build(self) -> CreateTaskFollowerRequest:
        return self._create_task_follower_request