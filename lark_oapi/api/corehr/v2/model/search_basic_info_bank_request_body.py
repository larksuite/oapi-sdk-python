# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class SearchBasicInfoBankRequestBody(object):
    _types = {
        "bank_id_list": List[str],
        "bank_name_list": List[str],
        "status_list": List[int],
    }

    def __init__(self, d=None):
        self.bank_id_list: Optional[List[str]] = None
        self.bank_name_list: Optional[List[str]] = None
        self.status_list: Optional[List[int]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchBasicInfoBankRequestBodyBuilder":
        return SearchBasicInfoBankRequestBodyBuilder()


class SearchBasicInfoBankRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._search_basic_info_bank_request_body = SearchBasicInfoBankRequestBody()

    def bank_id_list(self, bank_id_list: List[str]) -> "SearchBasicInfoBankRequestBodyBuilder":
        self._search_basic_info_bank_request_body.bank_id_list = bank_id_list
        return self

    def bank_name_list(self, bank_name_list: List[str]) -> "SearchBasicInfoBankRequestBodyBuilder":
        self._search_basic_info_bank_request_body.bank_name_list = bank_name_list
        return self

    def status_list(self, status_list: List[int]) -> "SearchBasicInfoBankRequestBodyBuilder":
        self._search_basic_info_bank_request_body.status_list = status_list
        return self

    def build(self) -> "SearchBasicInfoBankRequestBody":
        return self._search_basic_info_bank_request_body
