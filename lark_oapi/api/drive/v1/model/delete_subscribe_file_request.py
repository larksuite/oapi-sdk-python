# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class DeleteSubscribeFileRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.file_type: Optional[str] = None
        self.event_type: Optional[str] = None
        self.file_token: Optional[str] = None

    @staticmethod
    def builder() -> "DeleteSubscribeFileRequestBuilder":
        return DeleteSubscribeFileRequestBuilder()


class DeleteSubscribeFileRequestBuilder(object):

    def __init__(self) -> None:
        delete_subscribe_file_request = DeleteSubscribeFileRequest()
        delete_subscribe_file_request.http_method = HttpMethod.DELETE
        delete_subscribe_file_request.uri = "/open-apis/drive/v1/files/:file_token/delete_subscribe"
        delete_subscribe_file_request.token_types = {AccessTokenType.USER, AccessTokenType.TENANT}
        self._delete_subscribe_file_request: DeleteSubscribeFileRequest = delete_subscribe_file_request

    def file_type(self, file_type: str) -> "DeleteSubscribeFileRequestBuilder":
        self._delete_subscribe_file_request.file_type = file_type
        self._delete_subscribe_file_request.add_query("file_type", file_type)
        return self

    def event_type(self, event_type: str) -> "DeleteSubscribeFileRequestBuilder":
        self._delete_subscribe_file_request.event_type = event_type
        self._delete_subscribe_file_request.add_query("event_type", event_type)
        return self

    def file_token(self, file_token: str) -> "DeleteSubscribeFileRequestBuilder":
        self._delete_subscribe_file_request.file_token = file_token
        self._delete_subscribe_file_request.paths["file_token"] = str(file_token)
        return self

    def build(self) -> DeleteSubscribeFileRequest:
        return self._delete_subscribe_file_request
