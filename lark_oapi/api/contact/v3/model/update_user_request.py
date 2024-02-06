# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest
from .user import User


class UpdateUserRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.department_id_type: Optional[str] = None
        self.user_id: Optional[str] = None
        self.request_body: Optional[User] = None

    @staticmethod
    def builder() -> "UpdateUserRequestBuilder":
        return UpdateUserRequestBuilder()


class UpdateUserRequestBuilder(object):

    def __init__(self) -> None:
        update_user_request = UpdateUserRequest()
        update_user_request.http_method = HttpMethod.PUT
        update_user_request.uri = "/open-apis/contact/v3/users/:user_id"
        update_user_request.token_types = {AccessTokenType.TENANT}
        self._update_user_request: UpdateUserRequest = update_user_request

    def user_id_type(self, user_id_type: str) -> "UpdateUserRequestBuilder":
        self._update_user_request.user_id_type = user_id_type
        self._update_user_request.add_query("user_id_type", user_id_type)
        return self

    def department_id_type(self, department_id_type: str) -> "UpdateUserRequestBuilder":
        self._update_user_request.department_id_type = department_id_type
        self._update_user_request.add_query("department_id_type", department_id_type)
        return self

    def user_id(self, user_id: str) -> "UpdateUserRequestBuilder":
        self._update_user_request.user_id = user_id
        self._update_user_request.paths["user_id"] = str(user_id)
        return self

    def request_body(self, request_body: User) -> "UpdateUserRequestBuilder":
        self._update_user_request.request_body = request_body
        self._update_user_request.body = request_body
        return self

    def build(self) -> UpdateUserRequest:
        return self._update_user_request