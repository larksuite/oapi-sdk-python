# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest
from .list_ticket_customized_field_request_body import ListTicketCustomizedFieldRequestBody


class ListTicketCustomizedFieldRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None
        self.request_body: Optional[ListTicketCustomizedFieldRequestBody] = None

    @staticmethod
    def builder() -> "ListTicketCustomizedFieldRequestBuilder":
        return ListTicketCustomizedFieldRequestBuilder()


class ListTicketCustomizedFieldRequestBuilder(object):

    def __init__(self) -> None:
        list_ticket_customized_field_request = ListTicketCustomizedFieldRequest()
        list_ticket_customized_field_request.http_method = HttpMethod.GET
        list_ticket_customized_field_request.uri = "/open-apis/helpdesk/v1/ticket_customized_fields"
        list_ticket_customized_field_request.token_types = {AccessTokenType.TENANT}
        self._list_ticket_customized_field_request: ListTicketCustomizedFieldRequest = list_ticket_customized_field_request

    def page_token(self, page_token: str) -> "ListTicketCustomizedFieldRequestBuilder":
        self._list_ticket_customized_field_request.page_token = page_token
        self._list_ticket_customized_field_request.add_query("page_token", page_token)
        return self

    def page_size(self, page_size: int) -> "ListTicketCustomizedFieldRequestBuilder":
        self._list_ticket_customized_field_request.page_size = page_size
        self._list_ticket_customized_field_request.add_query("page_size", page_size)
        return self

    def request_body(self,
                     request_body: ListTicketCustomizedFieldRequestBody) -> "ListTicketCustomizedFieldRequestBuilder":
        self._list_ticket_customized_field_request.request_body = request_body
        self._list_ticket_customized_field_request.body = request_body
        return self

    def build(self) -> ListTicketCustomizedFieldRequest:
        return self._list_ticket_customized_field_request