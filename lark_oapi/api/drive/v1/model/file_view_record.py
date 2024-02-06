# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class FileViewRecord(object):
    _types = {
        "viewer_id": str,
        "name": str,
        "avatar_url": str,
        "last_view_time": str,
    }

    def __init__(self, d=None):
        self.viewer_id: Optional[str] = None
        self.name: Optional[str] = None
        self.avatar_url: Optional[str] = None
        self.last_view_time: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FileViewRecordBuilder":
        return FileViewRecordBuilder()


class FileViewRecordBuilder(object):
    def __init__(self) -> None:
        self._file_view_record = FileViewRecord()

    def viewer_id(self, viewer_id: str) -> "FileViewRecordBuilder":
        self._file_view_record.viewer_id = viewer_id
        return self

    def name(self, name: str) -> "FileViewRecordBuilder":
        self._file_view_record.name = name
        return self

    def avatar_url(self, avatar_url: str) -> "FileViewRecordBuilder":
        self._file_view_record.avatar_url = avatar_url
        return self

    def last_view_time(self, last_view_time: str) -> "FileViewRecordBuilder":
        self._file_view_record.last_view_time = last_view_time
        return self

    def build(self) -> "FileViewRecord":
        return self._file_view_record