# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListInterviewFeedbackFormRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.interview_feedback_form_ids: Optional[List[str]] = None
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None

    @staticmethod
    def builder() -> "ListInterviewFeedbackFormRequestBuilder":
        return ListInterviewFeedbackFormRequestBuilder()


class ListInterviewFeedbackFormRequestBuilder(object):

    def __init__(self) -> None:
        list_interview_feedback_form_request = ListInterviewFeedbackFormRequest()
        list_interview_feedback_form_request.http_method = HttpMethod.GET
        list_interview_feedback_form_request.uri = "/open-apis/hire/v1/interview_feedback_forms"
        list_interview_feedback_form_request.token_types = {AccessTokenType.TENANT}
        self._list_interview_feedback_form_request: ListInterviewFeedbackFormRequest = list_interview_feedback_form_request

    def interview_feedback_form_ids(self, interview_feedback_form_ids: List[
        str]) -> "ListInterviewFeedbackFormRequestBuilder":
        self._list_interview_feedback_form_request.interview_feedback_form_ids = interview_feedback_form_ids
        self._list_interview_feedback_form_request.add_query("interview_feedback_form_ids", interview_feedback_form_ids)
        return self

    def page_size(self, page_size: int) -> "ListInterviewFeedbackFormRequestBuilder":
        self._list_interview_feedback_form_request.page_size = page_size
        self._list_interview_feedback_form_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListInterviewFeedbackFormRequestBuilder":
        self._list_interview_feedback_form_request.page_token = page_token
        self._list_interview_feedback_form_request.add_query("page_token", page_token)
        return self

    def build(self) -> ListInterviewFeedbackFormRequest:
        return self._list_interview_feedback_form_request
