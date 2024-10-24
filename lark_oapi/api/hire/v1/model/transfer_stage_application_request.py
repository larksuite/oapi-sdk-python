# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .transfer_stage_application_request_body import TransferStageApplicationRequestBody


class TransferStageApplicationRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.application_id: Optional[str] = None
        self.request_body: Optional[TransferStageApplicationRequestBody] = None

    @staticmethod
    def builder() -> "TransferStageApplicationRequestBuilder":
        return TransferStageApplicationRequestBuilder()


class TransferStageApplicationRequestBuilder(object):

    def __init__(self) -> None:
        transfer_stage_application_request = TransferStageApplicationRequest()
        transfer_stage_application_request.http_method = HttpMethod.POST
        transfer_stage_application_request.uri = "/open-apis/hire/v1/applications/:application_id/transfer_stage"
        transfer_stage_application_request.token_types = {AccessTokenType.TENANT}
        self._transfer_stage_application_request: TransferStageApplicationRequest = transfer_stage_application_request

    def application_id(self, application_id: str) -> "TransferStageApplicationRequestBuilder":
        self._transfer_stage_application_request.application_id = application_id
        self._transfer_stage_application_request.paths["application_id"] = str(application_id)
        return self

    def request_body(self,
                     request_body: TransferStageApplicationRequestBody) -> "TransferStageApplicationRequestBuilder":
        self._transfer_stage_application_request.request_body = request_body
        self._transfer_stage_application_request.body = request_body
        return self

    def build(self) -> TransferStageApplicationRequest:
        return self._transfer_stage_application_request