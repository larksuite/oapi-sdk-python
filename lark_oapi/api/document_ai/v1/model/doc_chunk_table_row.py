# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .doc_chunk_table_cell import DocChunkTableCell


class DocChunkTableRow(object):
    _types = {
        "row_cells": List[DocChunkTableCell],
    }

    def __init__(self, d=None):
        self.row_cells: Optional[List[DocChunkTableCell]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DocChunkTableRowBuilder":
        return DocChunkTableRowBuilder()


class DocChunkTableRowBuilder(object):
    def __init__(self) -> None:
        self._doc_chunk_table_row = DocChunkTableRow()

    def row_cells(self, row_cells: List[DocChunkTableCell]) -> "DocChunkTableRowBuilder":
        self._doc_chunk_table_row.row_cells = row_cells
        return self

    def build(self) -> "DocChunkTableRow":
        return self._doc_chunk_table_row
