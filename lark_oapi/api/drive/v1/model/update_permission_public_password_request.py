# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class UpdatePermissionPublicPasswordRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.type: Optional[str] = None
        self.token: Optional[str] = None

    @staticmethod
    def builder() -> "UpdatePermissionPublicPasswordRequestBuilder":
        return UpdatePermissionPublicPasswordRequestBuilder()


class UpdatePermissionPublicPasswordRequestBuilder(object):

    def __init__(self) -> None:
        update_permission_public_password_request = UpdatePermissionPublicPasswordRequest()
        update_permission_public_password_request.http_method = HttpMethod.PUT
        update_permission_public_password_request.uri = "/open-apis/drive/v1/permissions/:token/public/password"
        update_permission_public_password_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._update_permission_public_password_request: UpdatePermissionPublicPasswordRequest = update_permission_public_password_request

    def type(self, type: str) -> "UpdatePermissionPublicPasswordRequestBuilder":
        self._update_permission_public_password_request.type = type
        self._update_permission_public_password_request.add_query("type", type)
        return self

    def token(self, token: str) -> "UpdatePermissionPublicPasswordRequestBuilder":
        self._update_permission_public_password_request.token = token
        self._update_permission_public_password_request.paths["token"] = str(token)
        return self

    def build(self) -> UpdatePermissionPublicPasswordRequest:
        return self._update_permission_public_password_request