# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .member import Member


class InputTasklist(object):
    _types = {
        "name": str,
        "client_token": str,
        "members": List[Member],
        "owner": Member,
    }

    def __init__(self, d=None):
        self.name: Optional[str] = None
        self.client_token: Optional[str] = None
        self.members: Optional[List[Member]] = None
        self.owner: Optional[Member] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "InputTasklistBuilder":
        return InputTasklistBuilder()


class InputTasklistBuilder(object):
    def __init__(self) -> None:
        self._input_tasklist = InputTasklist()

    def name(self, name: str) -> "InputTasklistBuilder":
        self._input_tasklist.name = name
        return self

    def client_token(self, client_token: str) -> "InputTasklistBuilder":
        self._input_tasklist.client_token = client_token
        return self

    def members(self, members: List[Member]) -> "InputTasklistBuilder":
        self._input_tasklist.members = members
        return self

    def owner(self, owner: Member) -> "InputTasklistBuilder":
        self._input_tasklist.owner = owner
        return self

    def build(self) -> "InputTasklist":
        return self._input_tasklist