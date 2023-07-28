# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from .member import Member


class RemoveMembersTasklistRequestBody(object):
    _types = {
        "members": List[Member],
    }

    def __init__(self, d=None):
        self.members: Optional[List[Member]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RemoveMembersTasklistRequestBodyBuilder":
        return RemoveMembersTasklistRequestBodyBuilder()


class RemoveMembersTasklistRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._remove_members_tasklist_request_body = RemoveMembersTasklistRequestBody()

    def members(self, members: List[Member]) -> "RemoveMembersTasklistRequestBodyBuilder":
        self._remove_members_tasklist_request_body.members = members
        return self

    def build(self) -> "RemoveMembersTasklistRequestBody":
        return self._remove_members_tasklist_request_body
