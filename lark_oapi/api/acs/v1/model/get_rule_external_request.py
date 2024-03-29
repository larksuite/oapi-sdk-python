# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class GetRuleExternalRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.device_id: Optional[int] = None
        self.user_id_type: Optional[str] = None

    @staticmethod
    def builder() -> "GetRuleExternalRequestBuilder":
        return GetRuleExternalRequestBuilder()


class GetRuleExternalRequestBuilder(object):

    def __init__(self) -> None:
        get_rule_external_request = GetRuleExternalRequest()
        get_rule_external_request.http_method = HttpMethod.GET
        get_rule_external_request.uri = "/open-apis/acs/v1/rule_external"
        get_rule_external_request.token_types = {AccessTokenType.USER}
        self._get_rule_external_request: GetRuleExternalRequest = get_rule_external_request

    def device_id(self, device_id: int) -> "GetRuleExternalRequestBuilder":
        self._get_rule_external_request.device_id = device_id
        self._get_rule_external_request.add_query("device_id", device_id)
        return self

    def user_id_type(self, user_id_type: str) -> "GetRuleExternalRequestBuilder":
        self._get_rule_external_request.user_id_type = user_id_type
        self._get_rule_external_request.add_query("user_id_type", user_id_type)
        return self

    def build(self) -> GetRuleExternalRequest:
        return self._get_rule_external_request
