# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .version import Version


class CreateFileVersionRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.file_token: Optional[str] = None
        self.request_body: Optional[Version] = None

    @staticmethod
    def builder() -> "CreateFileVersionRequestBuilder":
        return CreateFileVersionRequestBuilder()


class CreateFileVersionRequestBuilder(object):

    def __init__(self, create_file_version_request: CreateFileVersionRequest = CreateFileVersionRequest()) -> None:
        create_file_version_request.http_method = HttpMethod.POST
        create_file_version_request.uri = "/open-apis/drive/v1/files/:file_token/versions"
        create_file_version_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._create_file_version_request: CreateFileVersionRequest = create_file_version_request
    
    def user_id_type(self, user_id_type: str) -> "CreateFileVersionRequestBuilder":
        self._create_file_version_request.user_id_type = user_id_type
        self._create_file_version_request.queries["user_id_type"] = str(user_id_type)
        return self
    
    def file_token(self, file_token: str) -> "CreateFileVersionRequestBuilder":
        self._create_file_version_request.file_token = file_token
        self._create_file_version_request.paths["file_token"] = file_token
        return self
    
    def request_body(self, request_body: Version) -> "CreateFileVersionRequestBuilder":
        self._create_file_version_request.request_body = request_body
        self._create_file_version_request.body = request_body
        return self

    def build(self) -> CreateFileVersionRequest:
        return self._create_file_version_request