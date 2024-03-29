# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class AppCollaborator(object):
    _types = {
        "type": str,
        "user_id": str,
    }

    def __init__(self, d=None):
        self.type: Optional[str] = None
        self.user_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AppCollaboratorBuilder":
        return AppCollaboratorBuilder()


class AppCollaboratorBuilder(object):
    def __init__(self) -> None:
        self._app_collaborator = AppCollaborator()

    def type(self, type: str) -> "AppCollaboratorBuilder":
        self._app_collaborator.type = type
        return self

    def user_id(self, user_id: str) -> "AppCollaboratorBuilder":
        self._app_collaborator.user_id = user_id
        return self

    def build(self) -> "AppCollaborator":
        return self._app_collaborator
