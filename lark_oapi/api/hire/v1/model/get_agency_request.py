# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class GetAgencyRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.agency_id: Optional[str] = None

    @staticmethod
    def builder() -> "GetAgencyRequestBuilder":
        return GetAgencyRequestBuilder()


class GetAgencyRequestBuilder(object):

    def __init__(self) -> None:
        get_agency_request = GetAgencyRequest()
        get_agency_request.http_method = HttpMethod.GET
        get_agency_request.uri = "/open-apis/hire/v1/agencies/:agency_id"
        get_agency_request.token_types = {AccessTokenType.TENANT}
        self._get_agency_request: GetAgencyRequest = get_agency_request

    def user_id_type(self, user_id_type: str) -> "GetAgencyRequestBuilder":
        self._get_agency_request.user_id_type = user_id_type
        self._get_agency_request.add_query("user_id_type", user_id_type)
        return self

    def agency_id(self, agency_id: str) -> "GetAgencyRequestBuilder":
        self._get_agency_request.agency_id = agency_id
        self._get_agency_request.paths["agency_id"] = str(agency_id)
        return self

    def build(self) -> GetAgencyRequest:
        return self._get_agency_request