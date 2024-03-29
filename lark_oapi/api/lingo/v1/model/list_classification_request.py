# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListClassificationRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.repo_id: Optional[int] = None

    @staticmethod
    def builder() -> "ListClassificationRequestBuilder":
        return ListClassificationRequestBuilder()


class ListClassificationRequestBuilder(object):

    def __init__(self) -> None:
        list_classification_request = ListClassificationRequest()
        list_classification_request.http_method = HttpMethod.GET
        list_classification_request.uri = "/open-apis/lingo/v1/classifications"
        list_classification_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._list_classification_request: ListClassificationRequest = list_classification_request

    def page_size(self, page_size: int) -> "ListClassificationRequestBuilder":
        self._list_classification_request.page_size = page_size
        self._list_classification_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListClassificationRequestBuilder":
        self._list_classification_request.page_token = page_token
        self._list_classification_request.add_query("page_token", page_token)
        return self

    def repo_id(self, repo_id: int) -> "ListClassificationRequestBuilder":
        self._list_classification_request.repo_id = repo_id
        self._list_classification_request.add_query("repo_id", repo_id)
        return self

    def build(self) -> ListClassificationRequest:
        return self._list_classification_request
