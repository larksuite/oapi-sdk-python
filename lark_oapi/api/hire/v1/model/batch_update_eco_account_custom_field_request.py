# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .eco_account_custom_field import EcoAccountCustomField


class BatchUpdateEcoAccountCustomFieldRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[EcoAccountCustomField] = None

    @staticmethod
    def builder() -> "BatchUpdateEcoAccountCustomFieldRequestBuilder":
        return BatchUpdateEcoAccountCustomFieldRequestBuilder()


class BatchUpdateEcoAccountCustomFieldRequestBuilder(object):

    def __init__(self) -> None:
        batch_update_eco_account_custom_field_request = BatchUpdateEcoAccountCustomFieldRequest()
        batch_update_eco_account_custom_field_request.http_method = HttpMethod.PATCH
        batch_update_eco_account_custom_field_request.uri = "/open-apis/hire/v1/eco_account_custom_fields/batch_update"
        batch_update_eco_account_custom_field_request.token_types = {AccessTokenType.TENANT}
        self._batch_update_eco_account_custom_field_request: BatchUpdateEcoAccountCustomFieldRequest = batch_update_eco_account_custom_field_request

    def request_body(self, request_body: EcoAccountCustomField) -> "BatchUpdateEcoAccountCustomFieldRequestBuilder":
        self._batch_update_eco_account_custom_field_request.request_body = request_body
        self._batch_update_eco_account_custom_field_request.body = request_body
        return self

    def build(self) -> BatchUpdateEcoAccountCustomFieldRequest:
        return self._batch_update_eco_account_custom_field_request
