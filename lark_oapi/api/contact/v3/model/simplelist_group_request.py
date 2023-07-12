# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class SimplelistGroupRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.type: Optional[int] = None

    @staticmethod
    def builder() -> "SimplelistGroupRequestBuilder":
        return SimplelistGroupRequestBuilder()


class SimplelistGroupRequestBuilder(object):

    def __init__(self, simplelist_group_request: SimplelistGroupRequest = SimplelistGroupRequest()) -> None:
        simplelist_group_request.http_method = HttpMethod.GET
        simplelist_group_request.uri = "/open-apis/contact/v3/group/simplelist"
        simplelist_group_request.token_types = {AccessTokenType.TENANT}
        self._simplelist_group_request: SimplelistGroupRequest = simplelist_group_request
    
    def page_size(self, page_size: int) -> "SimplelistGroupRequestBuilder":
        self._simplelist_group_request.page_size = page_size
        self._simplelist_group_request.queries["page_size"] = str(page_size)
        return self
    
    def page_token(self, page_token: str) -> "SimplelistGroupRequestBuilder":
        self._simplelist_group_request.page_token = page_token
        self._simplelist_group_request.queries["page_token"] = str(page_token)
        return self
    
    def type(self, type: int) -> "SimplelistGroupRequestBuilder":
        self._simplelist_group_request.type = type
        self._simplelist_group_request.queries["type"] = str(type)
        return self
    

    def build(self) -> SimplelistGroupRequest:
        return self._simplelist_group_request