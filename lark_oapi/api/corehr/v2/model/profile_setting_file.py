# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class ProfileSettingFile(object):
    _types = {
        "file_id": str,
        "mime_type": str,
        "name": str,
        "size": int,
        "token": str,
    }

    def __init__(self, d=None):
        self.file_id: Optional[str] = None
        self.mime_type: Optional[str] = None
        self.name: Optional[str] = None
        self.size: Optional[int] = None
        self.token: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ProfileSettingFileBuilder":
        return ProfileSettingFileBuilder()


class ProfileSettingFileBuilder(object):
    def __init__(self) -> None:
        self._profile_setting_file = ProfileSettingFile()

    def file_id(self, file_id: str) -> "ProfileSettingFileBuilder":
        self._profile_setting_file.file_id = file_id
        return self

    def mime_type(self, mime_type: str) -> "ProfileSettingFileBuilder":
        self._profile_setting_file.mime_type = mime_type
        return self

    def name(self, name: str) -> "ProfileSettingFileBuilder":
        self._profile_setting_file.name = name
        return self

    def size(self, size: int) -> "ProfileSettingFileBuilder":
        self._profile_setting_file.size = size
        return self

    def token(self, token: str) -> "ProfileSettingFileBuilder":
        self._profile_setting_file.token = token
        return self

    def build(self) -> "ProfileSettingFile":
        return self._profile_setting_file
