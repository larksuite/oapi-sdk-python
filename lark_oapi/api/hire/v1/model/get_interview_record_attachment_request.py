# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class GetInterviewRecordAttachmentRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.application_id: Optional[str] = None
        self.interview_record_id: Optional[str] = None
        self.language: Optional[int] = None

    @staticmethod
    def builder() -> "GetInterviewRecordAttachmentRequestBuilder":
        return GetInterviewRecordAttachmentRequestBuilder()


class GetInterviewRecordAttachmentRequestBuilder(object):

    def __init__(self) -> None:
        get_interview_record_attachment_request = GetInterviewRecordAttachmentRequest()
        get_interview_record_attachment_request.http_method = HttpMethod.GET
        get_interview_record_attachment_request.uri = "/open-apis/hire/v1/interview_records/attachments"
        get_interview_record_attachment_request.token_types = {AccessTokenType.TENANT}
        self._get_interview_record_attachment_request: GetInterviewRecordAttachmentRequest = get_interview_record_attachment_request

    def application_id(self, application_id: str) -> "GetInterviewRecordAttachmentRequestBuilder":
        self._get_interview_record_attachment_request.application_id = application_id
        self._get_interview_record_attachment_request.add_query("application_id", application_id)
        return self

    def interview_record_id(self, interview_record_id: str) -> "GetInterviewRecordAttachmentRequestBuilder":
        self._get_interview_record_attachment_request.interview_record_id = interview_record_id
        self._get_interview_record_attachment_request.add_query("interview_record_id", interview_record_id)
        return self

    def language(self, language: int) -> "GetInterviewRecordAttachmentRequestBuilder":
        self._get_interview_record_attachment_request.language = language
        self._get_interview_record_attachment_request.add_query("language", language)
        return self

    def build(self) -> GetInterviewRecordAttachmentRequest:
        return self._get_interview_record_attachment_request
