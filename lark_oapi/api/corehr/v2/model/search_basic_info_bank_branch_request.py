# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .search_basic_info_bank_branch_request_body import SearchBasicInfoBankBranchRequestBody


class SearchBasicInfoBankBranchRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.request_body: Optional[SearchBasicInfoBankBranchRequestBody] = None

    @staticmethod
    def builder() -> "SearchBasicInfoBankBranchRequestBuilder":
        return SearchBasicInfoBankBranchRequestBuilder()


class SearchBasicInfoBankBranchRequestBuilder(object):

    def __init__(self) -> None:
        search_basic_info_bank_branch_request = SearchBasicInfoBankBranchRequest()
        search_basic_info_bank_branch_request.http_method = HttpMethod.POST
        search_basic_info_bank_branch_request.uri = "/open-apis/corehr/v2/basic_info/bank_branchs/search"
        search_basic_info_bank_branch_request.token_types = {AccessTokenType.TENANT}
        self._search_basic_info_bank_branch_request: SearchBasicInfoBankBranchRequest = search_basic_info_bank_branch_request

    def page_size(self, page_size: int) -> "SearchBasicInfoBankBranchRequestBuilder":
        self._search_basic_info_bank_branch_request.page_size = page_size
        self._search_basic_info_bank_branch_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "SearchBasicInfoBankBranchRequestBuilder":
        self._search_basic_info_bank_branch_request.page_token = page_token
        self._search_basic_info_bank_branch_request.add_query("page_token", page_token)
        return self

    def request_body(self,
                     request_body: SearchBasicInfoBankBranchRequestBody) -> "SearchBasicInfoBankBranchRequestBuilder":
        self._search_basic_info_bank_branch_request.request_body = request_body
        self._search_basic_info_bank_branch_request.body = request_body
        return self

    def build(self) -> SearchBasicInfoBankBranchRequest:
        return self._search_basic_info_bank_branch_request
