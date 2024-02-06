# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class ListSectionRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.resource_type: Optional[str] = None
        self.resource_id: Optional[str] = None
        self.user_id_type: Optional[str] = None

    @staticmethod
    def builder() -> "ListSectionRequestBuilder":
        return ListSectionRequestBuilder()


class ListSectionRequestBuilder(object):

    def __init__(self) -> None:
        list_section_request = ListSectionRequest()
        list_section_request.http_method = HttpMethod.GET
        list_section_request.uri = "/open-apis/task/v2/sections"
        list_section_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._list_section_request: ListSectionRequest = list_section_request

    def page_size(self, page_size: int) -> "ListSectionRequestBuilder":
        self._list_section_request.page_size = page_size
        self._list_section_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListSectionRequestBuilder":
        self._list_section_request.page_token = page_token
        self._list_section_request.add_query("page_token", page_token)
        return self

    def resource_type(self, resource_type: str) -> "ListSectionRequestBuilder":
        self._list_section_request.resource_type = resource_type
        self._list_section_request.add_query("resource_type", resource_type)
        return self

    def resource_id(self, resource_id: str) -> "ListSectionRequestBuilder":
        self._list_section_request.resource_id = resource_id
        self._list_section_request.add_query("resource_id", resource_id)
        return self

    def user_id_type(self, user_id_type: str) -> "ListSectionRequestBuilder":
        self._list_section_request.user_id_type = user_id_type
        self._list_section_request.add_query("user_id_type", user_id_type)
        return self

    def build(self) -> ListSectionRequest:
        return self._list_section_request