# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .member import Member


class Tasklist(object):
    _types = {
        "guid": str,
        "name": str,
        "creator": Member,
        "owner": Member,
        "members": List[Member],
        "url": str,
        "created_at": int,
        "updated_at": int,
    }

    def __init__(self, d=None):
        self.guid: Optional[str] = None
        self.name: Optional[str] = None
        self.creator: Optional[Member] = None
        self.owner: Optional[Member] = None
        self.members: Optional[List[Member]] = None
        self.url: Optional[str] = None
        self.created_at: Optional[int] = None
        self.updated_at: Optional[int] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TasklistBuilder":
        return TasklistBuilder()


class TasklistBuilder(object):
    def __init__(self) -> None:
        self._tasklist = Tasklist()

    def guid(self, guid: str) -> "TasklistBuilder":
        self._tasklist.guid = guid
        return self

    def name(self, name: str) -> "TasklistBuilder":
        self._tasklist.name = name
        return self

    def creator(self, creator: Member) -> "TasklistBuilder":
        self._tasklist.creator = creator
        return self

    def owner(self, owner: Member) -> "TasklistBuilder":
        self._tasklist.owner = owner
        return self

    def members(self, members: List[Member]) -> "TasklistBuilder":
        self._tasklist.members = members
        return self

    def url(self, url: str) -> "TasklistBuilder":
        self._tasklist.url = url
        return self

    def created_at(self, created_at: int) -> "TasklistBuilder":
        self._tasklist.created_at = created_at
        return self

    def updated_at(self, updated_at: int) -> "TasklistBuilder":
        self._tasklist.updated_at = updated_at
        return self

    def build(self) -> "Tasklist":
        return self._tasklist