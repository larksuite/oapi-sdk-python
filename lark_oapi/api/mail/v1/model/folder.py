# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class Folder(object):
    _types = {
        "id": str,
        "name": str,
        "parent_folder_id": int,
        "folder_type": int,
        "unread_message_count": int,
        "unread_thread_count": int,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.parent_folder_id: Optional[int] = None
        self.folder_type: Optional[int] = None
        self.unread_message_count: Optional[int] = None
        self.unread_thread_count: Optional[int] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FolderBuilder":
        return FolderBuilder()


class FolderBuilder(object):
    def __init__(self) -> None:
        self._folder = Folder()

    def id(self, id: str) -> "FolderBuilder":
        self._folder.id = id
        return self

    def name(self, name: str) -> "FolderBuilder":
        self._folder.name = name
        return self

    def parent_folder_id(self, parent_folder_id: int) -> "FolderBuilder":
        self._folder.parent_folder_id = parent_folder_id
        return self

    def folder_type(self, folder_type: int) -> "FolderBuilder":
        self._folder.folder_type = folder_type
        return self

    def unread_message_count(self, unread_message_count: int) -> "FolderBuilder":
        self._folder.unread_message_count = unread_message_count
        return self

    def unread_thread_count(self, unread_thread_count: int) -> "FolderBuilder":
        self._folder.unread_thread_count = unread_thread_count
        return self

    def build(self) -> "Folder":
        return self._folder
