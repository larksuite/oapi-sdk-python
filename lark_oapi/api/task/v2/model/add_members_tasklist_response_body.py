# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from .tasklist import Tasklist


class AddMembersTasklistResponseBody(object):
    _types = {
        "tasklist": Tasklist,
    }

    def __init__(self, d=None):
        self.tasklist: Optional[Tasklist] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AddMembersTasklistResponseBodyBuilder":
        return AddMembersTasklistResponseBodyBuilder()


class AddMembersTasklistResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._add_members_tasklist_response_body = AddMembersTasklistResponseBody()

    def tasklist(self, tasklist: Tasklist) -> "AddMembersTasklistResponseBodyBuilder":
        self._add_members_tasklist_response_body.tasklist = tasklist
        return self

    def build(self) -> "AddMembersTasklistResponseBody":
        return self._add_members_tasklist_response_body
