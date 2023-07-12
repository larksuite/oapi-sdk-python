# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class GetProgressRecordRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.progress_id: Optional[int] = None

    @staticmethod
    def builder() -> "GetProgressRecordRequestBuilder":
        return GetProgressRecordRequestBuilder()


class GetProgressRecordRequestBuilder(object):

    def __init__(self, get_progress_record_request: GetProgressRecordRequest = GetProgressRecordRequest()) -> None:
        get_progress_record_request.http_method = HttpMethod.GET
        get_progress_record_request.uri = "/open-apis/okr/v1/progress_records/:progress_id"
        get_progress_record_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._get_progress_record_request: GetProgressRecordRequest = get_progress_record_request
    
    def user_id_type(self, user_id_type: str) -> "GetProgressRecordRequestBuilder":
        self._get_progress_record_request.user_id_type = user_id_type
        self._get_progress_record_request.queries["user_id_type"] = str(user_id_type)
        return self
    
    def progress_id(self, progress_id: int) -> "GetProgressRecordRequestBuilder":
        self._get_progress_record_request.progress_id = progress_id
        self._get_progress_record_request.paths["progress_id"] = progress_id
        return self
    

    def build(self) -> GetProgressRecordRequest:
        return self._get_progress_record_request