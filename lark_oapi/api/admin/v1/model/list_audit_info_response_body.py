# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .audit_info import AuditInfo


class ListAuditInfoResponseBody(object):
    _types = {
        "has_more": bool,
        "page_token": str,
        "items": List[AuditInfo],
    }

    def __init__(self, d=None):
        self.has_more: Optional[bool] = None
        self.page_token: Optional[str] = None
        self.items: Optional[List[AuditInfo]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ListAuditInfoResponseBodyBuilder":
        return ListAuditInfoResponseBodyBuilder()


class ListAuditInfoResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._list_audit_info_response_body = ListAuditInfoResponseBody()

    def has_more(self, has_more: bool) -> "ListAuditInfoResponseBodyBuilder":
        self._list_audit_info_response_body.has_more = has_more
        return self

    def page_token(self, page_token: str) -> "ListAuditInfoResponseBodyBuilder":
        self._list_audit_info_response_body.page_token = page_token
        return self

    def items(self, items: List[AuditInfo]) -> "ListAuditInfoResponseBodyBuilder":
        self._list_audit_info_response_body.items = items
        return self

    def build(self) -> "ListAuditInfoResponseBody":
        return self._list_audit_info_response_body