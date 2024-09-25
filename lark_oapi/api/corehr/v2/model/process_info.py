# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class ProcessInfo(object):
    _types = {
        "process_id": str,
        "approval_group_status": str,
    }

    def __init__(self, d=None):
        self.process_id: Optional[str] = None
        self.approval_group_status: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ProcessInfoBuilder":
        return ProcessInfoBuilder()


class ProcessInfoBuilder(object):
    def __init__(self) -> None:
        self._process_info = ProcessInfo()

    def process_id(self, process_id: str) -> "ProcessInfoBuilder":
        self._process_info.process_id = process_id
        return self

    def approval_group_status(self, approval_group_status: str) -> "ProcessInfoBuilder":
        self._process_info.approval_group_status = approval_group_status
        return self

    def build(self) -> "ProcessInfo":
        return self._process_info
