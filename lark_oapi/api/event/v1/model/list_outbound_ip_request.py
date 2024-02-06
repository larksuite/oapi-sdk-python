# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class ListOutboundIpRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None

    @staticmethod
    def builder() -> "ListOutboundIpRequestBuilder":
        return ListOutboundIpRequestBuilder()


class ListOutboundIpRequestBuilder(object):

    def __init__(self) -> None:
        list_outbound_ip_request = ListOutboundIpRequest()
        list_outbound_ip_request.http_method = HttpMethod.GET
        list_outbound_ip_request.uri = "/open-apis/event/v1/outbound_ip"
        list_outbound_ip_request.token_types = {AccessTokenType.TENANT}
        self._list_outbound_ip_request: ListOutboundIpRequest = list_outbound_ip_request

    def page_size(self, page_size: int) -> "ListOutboundIpRequestBuilder":
        self._list_outbound_ip_request.page_size = page_size
        self._list_outbound_ip_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListOutboundIpRequestBuilder":
        self._list_outbound_ip_request.page_token = page_token
        self._list_outbound_ip_request.add_query("page_token", page_token)
        return self

    def build(self) -> ListOutboundIpRequest:
        return self._list_outbound_ip_request