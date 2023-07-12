# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .filter_view import FilterView


class PatchSpreadsheetSheetFilterViewResponseBody(object):
    _types = {
        "filter_view": FilterView,
    }

    def __init__(self, d):
        self.filter_view: Optional[FilterView] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PatchSpreadsheetSheetFilterViewResponseBodyBuilder":
        return PatchSpreadsheetSheetFilterViewResponseBodyBuilder()


class PatchSpreadsheetSheetFilterViewResponseBodyBuilder(object):
    def __init__(self, patch_spreadsheet_sheet_filter_view_response_body: PatchSpreadsheetSheetFilterViewResponseBody = PatchSpreadsheetSheetFilterViewResponseBody({})) -> None:
        self._patch_spreadsheet_sheet_filter_view_response_body: PatchSpreadsheetSheetFilterViewResponseBody = patch_spreadsheet_sheet_filter_view_response_body
    
    def filter_view(self, filter_view: FilterView) -> "PatchSpreadsheetSheetFilterViewResponseBodyBuilder":
        self._patch_spreadsheet_sheet_filter_view_response_body.filter_view = filter_view
        return self
    
    def build(self) -> "PatchSpreadsheetSheetFilterViewResponseBody":
        return self._patch_spreadsheet_sheet_filter_view_response_body