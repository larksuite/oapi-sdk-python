# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .recognize_taxi_invoice_request_body import RecognizeTaxiInvoiceRequestBody


class RecognizeTaxiInvoiceRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[RecognizeTaxiInvoiceRequestBody] = None

    @staticmethod
    def builder() -> "RecognizeTaxiInvoiceRequestBuilder":
        return RecognizeTaxiInvoiceRequestBuilder()


class RecognizeTaxiInvoiceRequestBuilder(object):

    def __init__(self) -> None:
        recognize_taxi_invoice_request = RecognizeTaxiInvoiceRequest()
        recognize_taxi_invoice_request.http_method = HttpMethod.POST
        recognize_taxi_invoice_request.uri = "/open-apis/document_ai/v1/taxi_invoice/recognize"
        recognize_taxi_invoice_request.token_types = {AccessTokenType.TENANT}
        self._recognize_taxi_invoice_request: RecognizeTaxiInvoiceRequest = recognize_taxi_invoice_request

    def request_body(self, request_body: RecognizeTaxiInvoiceRequestBody) -> "RecognizeTaxiInvoiceRequestBuilder":
        self._recognize_taxi_invoice_request.request_body = request_body
        self._recognize_taxi_invoice_request.body = request_body
        return self

    def build(self) -> RecognizeTaxiInvoiceRequest:
        return self._recognize_taxi_invoice_request
