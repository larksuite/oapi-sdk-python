# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class FileBlockChangeInfo(object):
    _types = {
        "block_token": str,
        "block_token_type": str,
        "rev_ranges": List[int],
    }

    def __init__(self, d=None):
        self.block_token: Optional[str] = None
        self.block_token_type: Optional[str] = None
        self.rev_ranges: Optional[List[int]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FileBlockChangeInfoBuilder":
        return FileBlockChangeInfoBuilder()


class FileBlockChangeInfoBuilder(object):
    def __init__(self) -> None:
        self._file_block_change_info = FileBlockChangeInfo()

    def block_token(self, block_token: str) -> "FileBlockChangeInfoBuilder":
        self._file_block_change_info.block_token = block_token
        return self

    def block_token_type(self, block_token_type: str) -> "FileBlockChangeInfoBuilder":
        self._file_block_change_info.block_token_type = block_token_type
        return self

    def rev_ranges(self, rev_ranges: List[int]) -> "FileBlockChangeInfoBuilder":
        self._file_block_change_info.rev_ranges = rev_ranges
        return self

    def build(self) -> "FileBlockChangeInfo":
        return self._file_block_change_info
