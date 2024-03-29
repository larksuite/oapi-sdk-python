# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .create_rule_external_request_body import CreateRuleExternalRequestBody


class CreateRuleExternalRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.rule_id: Optional[int] = None
        self.user_id_type: Optional[str] = None
        self.request_body: Optional[CreateRuleExternalRequestBody] = None

    @staticmethod
    def builder() -> "CreateRuleExternalRequestBuilder":
        return CreateRuleExternalRequestBuilder()


class CreateRuleExternalRequestBuilder(object):

    def __init__(self) -> None:
        create_rule_external_request = CreateRuleExternalRequest()
        create_rule_external_request.http_method = HttpMethod.POST
        create_rule_external_request.uri = "/open-apis/acs/v1/rule_external"
        create_rule_external_request.token_types = {AccessTokenType.USER}
        self._create_rule_external_request: CreateRuleExternalRequest = create_rule_external_request

    def rule_id(self, rule_id: int) -> "CreateRuleExternalRequestBuilder":
        self._create_rule_external_request.rule_id = rule_id
        self._create_rule_external_request.add_query("rule_id", rule_id)
        return self

    def user_id_type(self, user_id_type: str) -> "CreateRuleExternalRequestBuilder":
        self._create_rule_external_request.user_id_type = user_id_type
        self._create_rule_external_request.add_query("user_id_type", user_id_type)
        return self

    def request_body(self, request_body: CreateRuleExternalRequestBody) -> "CreateRuleExternalRequestBuilder":
        self._create_rule_external_request.request_body = request_body
        self._create_rule_external_request.body = request_body
        return self

    def build(self) -> CreateRuleExternalRequest:
        return self._create_rule_external_request
