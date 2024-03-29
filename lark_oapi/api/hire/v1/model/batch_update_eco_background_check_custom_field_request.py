# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .eco_background_check_custom_field import EcoBackgroundCheckCustomField


class BatchUpdateEcoBackgroundCheckCustomFieldRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[EcoBackgroundCheckCustomField] = None

    @staticmethod
    def builder() -> "BatchUpdateEcoBackgroundCheckCustomFieldRequestBuilder":
        return BatchUpdateEcoBackgroundCheckCustomFieldRequestBuilder()


class BatchUpdateEcoBackgroundCheckCustomFieldRequestBuilder(object):

    def __init__(self) -> None:
        batch_update_eco_background_check_custom_field_request = BatchUpdateEcoBackgroundCheckCustomFieldRequest()
        batch_update_eco_background_check_custom_field_request.http_method = HttpMethod.PATCH
        batch_update_eco_background_check_custom_field_request.uri = "/open-apis/hire/v1/eco_background_check_custom_fields/batch_update"
        batch_update_eco_background_check_custom_field_request.token_types = {AccessTokenType.TENANT}
        self._batch_update_eco_background_check_custom_field_request: BatchUpdateEcoBackgroundCheckCustomFieldRequest = batch_update_eco_background_check_custom_field_request

    def request_body(self,
                     request_body: EcoBackgroundCheckCustomField) -> "BatchUpdateEcoBackgroundCheckCustomFieldRequestBuilder":
        self._batch_update_eco_background_check_custom_field_request.request_body = request_body
        self._batch_update_eco_background_check_custom_field_request.body = request_body
        return self

    def build(self) -> BatchUpdateEcoBackgroundCheckCustomFieldRequest:
        return self._batch_update_eco_background_check_custom_field_request
