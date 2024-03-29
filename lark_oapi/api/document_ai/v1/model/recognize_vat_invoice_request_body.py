# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class RecognizeVatInvoiceRequestBody(object):
    _types = {
        "file": IO[Any],
    }

    def __init__(self, d=None):
        self.file: Optional[IO[Any]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RecognizeVatInvoiceRequestBodyBuilder":
        return RecognizeVatInvoiceRequestBodyBuilder()


class RecognizeVatInvoiceRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._recognize_vat_invoice_request_body = RecognizeVatInvoiceRequestBody()

    def file(self, file: IO[Any]) -> "RecognizeVatInvoiceRequestBodyBuilder":
        self._recognize_vat_invoice_request_body.file = file
        return self

    def build(self) -> "RecognizeVatInvoiceRequestBody":
        return self._recognize_vat_invoice_request_body
