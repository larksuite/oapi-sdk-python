# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class DeleteMailgroupRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.mailgroup_id: Optional[str] = None

    @staticmethod
    def builder() -> "DeleteMailgroupRequestBuilder":
        return DeleteMailgroupRequestBuilder()


class DeleteMailgroupRequestBuilder(object):

    def __init__(self) -> None:
        delete_mailgroup_request = DeleteMailgroupRequest()
        delete_mailgroup_request.http_method = HttpMethod.DELETE
        delete_mailgroup_request.uri = "/open-apis/mail/v1/mailgroups/:mailgroup_id"
        delete_mailgroup_request.token_types = {AccessTokenType.TENANT}
        self._delete_mailgroup_request: DeleteMailgroupRequest = delete_mailgroup_request

    def mailgroup_id(self, mailgroup_id: str) -> "DeleteMailgroupRequestBuilder":
        self._delete_mailgroup_request.mailgroup_id = mailgroup_id
        self._delete_mailgroup_request.paths["mailgroup_id"] = str(mailgroup_id)
        return self

    def build(self) -> DeleteMailgroupRequest:
        return self._delete_mailgroup_request
