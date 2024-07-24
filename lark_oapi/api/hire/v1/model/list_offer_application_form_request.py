# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListOfferApplicationFormRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None

    @staticmethod
    def builder() -> "ListOfferApplicationFormRequestBuilder":
        return ListOfferApplicationFormRequestBuilder()


class ListOfferApplicationFormRequestBuilder(object):

    def __init__(self) -> None:
        list_offer_application_form_request = ListOfferApplicationFormRequest()
        list_offer_application_form_request.http_method = HttpMethod.GET
        list_offer_application_form_request.uri = "/open-apis/hire/v1/offer_application_forms"
        list_offer_application_form_request.token_types = {AccessTokenType.TENANT}
        self._list_offer_application_form_request: ListOfferApplicationFormRequest = list_offer_application_form_request

    def page_token(self, page_token: str) -> "ListOfferApplicationFormRequestBuilder":
        self._list_offer_application_form_request.page_token = page_token
        self._list_offer_application_form_request.add_query("page_token", page_token)
        return self

    def page_size(self, page_size: int) -> "ListOfferApplicationFormRequestBuilder":
        self._list_offer_application_form_request.page_size = page_size
        self._list_offer_application_form_request.add_query("page_size", page_size)
        return self

    def build(self) -> ListOfferApplicationFormRequest:
        return self._list_offer_application_form_request
