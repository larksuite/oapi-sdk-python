# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListCalendarEventAttendeeRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None
        self.calendar_id: Optional[str] = None
        self.event_id: Optional[str] = None

    @staticmethod
    def builder() -> "ListCalendarEventAttendeeRequestBuilder":
        return ListCalendarEventAttendeeRequestBuilder()


class ListCalendarEventAttendeeRequestBuilder(object):

    def __init__(self, list_calendar_event_attendee_request: ListCalendarEventAttendeeRequest = ListCalendarEventAttendeeRequest()) -> None:
        list_calendar_event_attendee_request.http_method = HttpMethod.GET
        list_calendar_event_attendee_request.uri = "/open-apis/calendar/v4/calendars/:calendar_id/events/:event_id/attendees"
        list_calendar_event_attendee_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._list_calendar_event_attendee_request: ListCalendarEventAttendeeRequest = list_calendar_event_attendee_request
    
    def user_id_type(self, user_id_type: str) -> "ListCalendarEventAttendeeRequestBuilder":
        self._list_calendar_event_attendee_request.user_id_type = user_id_type
        self._list_calendar_event_attendee_request.queries["user_id_type"] = str(user_id_type)
        return self
    
    def page_token(self, page_token: str) -> "ListCalendarEventAttendeeRequestBuilder":
        self._list_calendar_event_attendee_request.page_token = page_token
        self._list_calendar_event_attendee_request.queries["page_token"] = str(page_token)
        return self
    
    def page_size(self, page_size: int) -> "ListCalendarEventAttendeeRequestBuilder":
        self._list_calendar_event_attendee_request.page_size = page_size
        self._list_calendar_event_attendee_request.queries["page_size"] = str(page_size)
        return self
    
    def calendar_id(self, calendar_id: str) -> "ListCalendarEventAttendeeRequestBuilder":
        self._list_calendar_event_attendee_request.calendar_id = calendar_id
        self._list_calendar_event_attendee_request.paths["calendar_id"] = calendar_id
        return self
    
    def event_id(self, event_id: str) -> "ListCalendarEventAttendeeRequestBuilder":
        self._list_calendar_event_attendee_request.event_id = event_id
        self._list_calendar_event_attendee_request.paths["event_id"] = event_id
        return self
    

    def build(self) -> ListCalendarEventAttendeeRequest:
        return self._list_calendar_event_attendee_request