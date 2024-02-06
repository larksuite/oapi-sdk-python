# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest


class ListCalendarAclRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None
        self.calendar_id: Optional[str] = None

    @staticmethod
    def builder() -> "ListCalendarAclRequestBuilder":
        return ListCalendarAclRequestBuilder()


class ListCalendarAclRequestBuilder(object):

    def __init__(self) -> None:
        list_calendar_acl_request = ListCalendarAclRequest()
        list_calendar_acl_request.http_method = HttpMethod.GET
        list_calendar_acl_request.uri = "/open-apis/calendar/v4/calendars/:calendar_id/acls"
        list_calendar_acl_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._list_calendar_acl_request: ListCalendarAclRequest = list_calendar_acl_request

    def user_id_type(self, user_id_type: str) -> "ListCalendarAclRequestBuilder":
        self._list_calendar_acl_request.user_id_type = user_id_type
        self._list_calendar_acl_request.add_query("user_id_type", user_id_type)
        return self

    def page_token(self, page_token: str) -> "ListCalendarAclRequestBuilder":
        self._list_calendar_acl_request.page_token = page_token
        self._list_calendar_acl_request.add_query("page_token", page_token)
        return self

    def page_size(self, page_size: int) -> "ListCalendarAclRequestBuilder":
        self._list_calendar_acl_request.page_size = page_size
        self._list_calendar_acl_request.add_query("page_size", page_size)
        return self

    def calendar_id(self, calendar_id: str) -> "ListCalendarAclRequestBuilder":
        self._list_calendar_acl_request.calendar_id = calendar_id
        self._list_calendar_acl_request.paths["calendar_id"] = str(calendar_id)
        return self

    def build(self) -> ListCalendarAclRequest:
        return self._list_calendar_acl_request