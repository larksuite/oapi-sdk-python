# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class SectionSummary(object):
    _types = {
        "guid": str,
        "name": str,
        "is_default": bool,
    }

    def __init__(self, d=None):
        self.guid: Optional[str] = None
        self.name: Optional[str] = None
        self.is_default: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SectionSummaryBuilder":
        return SectionSummaryBuilder()


class SectionSummaryBuilder(object):
    def __init__(self) -> None:
        self._section_summary = SectionSummary()

    def guid(self, guid: str) -> "SectionSummaryBuilder":
        self._section_summary.guid = guid
        return self

    def name(self, name: str) -> "SectionSummaryBuilder":
        self._section_summary.name = name
        return self

    def is_default(self, is_default: bool) -> "SectionSummaryBuilder":
        self._section_summary.is_default = is_default
        return self

    def build(self) -> "SectionSummary":
        return self._section_summary