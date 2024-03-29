# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .taxi_invoice import TaxiInvoice


class RecognizeTaxiInvoiceResponseBody(object):
    _types = {
        "taxi_invoices": List[TaxiInvoice],
    }

    def __init__(self, d=None):
        self.taxi_invoices: Optional[List[TaxiInvoice]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RecognizeTaxiInvoiceResponseBodyBuilder":
        return RecognizeTaxiInvoiceResponseBodyBuilder()


class RecognizeTaxiInvoiceResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._recognize_taxi_invoice_response_body = RecognizeTaxiInvoiceResponseBody()

    def taxi_invoices(self, taxi_invoices: List[TaxiInvoice]) -> "RecognizeTaxiInvoiceResponseBodyBuilder":
        self._recognize_taxi_invoice_response_body.taxi_invoices = taxi_invoices
        return self

    def build(self) -> "RecognizeTaxiInvoiceResponseBody":
        return self._recognize_taxi_invoice_response_body
