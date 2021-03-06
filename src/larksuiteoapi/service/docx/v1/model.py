# -*- coding: UTF-8 -*-
# Code generated by lark suite oapi sdk gen

from typing import List, Dict, Any
from ....utils.dt import to_json_decorator
import attr




@to_json_decorator
@attr.s
class View(object):
    view_type = attr.ib(type=int, default=None, metadata={'json': 'view_type'})


@to_json_decorator
@attr.s
class UpdateTablePropertyRequest(object):
    column_width = attr.ib(type=int, default=None, metadata={'json': 'column_width'})
    column_index = attr.ib(type=int, default=None, metadata={'json': 'column_index'})


@to_json_decorator
@attr.s
class UpdateGridColumnWidthRatioRequest(object):
    width_ratios = attr.ib(type=List[int], default=None, metadata={'json': 'width_ratios'})


@to_json_decorator
@attr.s
class UnmergeTableCellsRequest(object):
    row_index = attr.ib(type=int, default=None, metadata={'json': 'row_index'})
    column_index = attr.ib(type=int, default=None, metadata={'json': 'column_index'})


@to_json_decorator
@attr.s
class UndefinedElement(object):
    pass


@to_json_decorator
@attr.s
class Undefined(object):
    pass


@to_json_decorator
@attr.s
class TextStyle(object):
    align = attr.ib(type=int, default=None, metadata={'json': 'align'})
    done = attr.ib(type=bool, default=None, metadata={'json': 'done'})
    folded = attr.ib(type=bool, default=None, metadata={'json': 'folded'})
    language = attr.ib(type=int, default=None, metadata={'json': 'language'})
    wrap = attr.ib(type=bool, default=None, metadata={'json': 'wrap'})


@to_json_decorator
@attr.s
class UpdateTextStyleRequest(object):
    style = attr.ib(type=TextStyle, default=None, metadata={'json': 'style'})
    fields = attr.ib(type=List[int], default=None, metadata={'json': 'fields'})


@to_json_decorator
@attr.s
class TableMergeInfo(object):
    row_span = attr.ib(type=int, default=None, metadata={'json': 'row_span'})
    col_span = attr.ib(type=int, default=None, metadata={'json': 'col_span'})


@to_json_decorator
@attr.s
class TableProperty(object):
    row_size = attr.ib(type=int, default=None, metadata={'json': 'row_size'})
    column_size = attr.ib(type=int, default=None, metadata={'json': 'column_size'})
    column_width = attr.ib(type=List[int], default=None, metadata={'json': 'column_width'})
    merge_info = attr.ib(type=List[TableMergeInfo], default=None, metadata={'json': 'merge_info'})


@to_json_decorator
@attr.s
class Table(object):
    cells = attr.ib(type=List[str], default=None, metadata={'json': 'cells'})
    property = attr.ib(type=TableProperty, default=None, metadata={'json': 'property'})


@to_json_decorator
@attr.s
class TableCell(object):
    pass


@to_json_decorator
@attr.s
class Sheet(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    row_size = attr.ib(type=int, default=None, metadata={'json': 'row_size'})
    column_size = attr.ib(type=int, default=None, metadata={'json': 'column_size'})


@to_json_decorator
@attr.s
class ReplaceImageRequest(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})


@to_json_decorator
@attr.s
class ReplaceFileRequest(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})


@to_json_decorator
@attr.s
class Reminder(object):
    __int_to_string_fields__ = attr.ib(type=List[str], default=["expire_time", "notify_time"])
    create_user_id = attr.ib(type=str, default=None, metadata={'json': 'create_user_id'})
    is_notify = attr.ib(type=bool, default=None, metadata={'json': 'is_notify'})
    is_whole_day = attr.ib(type=bool, default=None, metadata={'json': 'is_whole_day'})
    expire_time = attr.ib(type=int, default=None, metadata={'json': 'expire_time'})
    notify_time = attr.ib(type=int, default=None, metadata={'json': 'notify_time'})


@to_json_decorator
@attr.s
class Mindnote(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})


@to_json_decorator
@attr.s
class MergeTableCellsRequest(object):
    row_start_index = attr.ib(type=int, default=None, metadata={'json': 'row_start_index'})
    row_end_index = attr.ib(type=int, default=None, metadata={'json': 'row_end_index'})
    column_start_index = attr.ib(type=int, default=None, metadata={'json': 'column_start_index'})
    column_end_index = attr.ib(type=int, default=None, metadata={'json': 'column_end_index'})


@to_json_decorator
@attr.s
class MentionUser(object):
    user_id = attr.ib(type=str, default=None, metadata={'json': 'user_id'})


@to_json_decorator
@attr.s
class MentionDoc(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    obj_type = attr.ib(type=int, default=None, metadata={'json': 'obj_type'})
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})
    title = attr.ib(type=str, default=None, metadata={'json': 'title'})


@to_json_decorator
@attr.s
class Link(object):
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})


@to_json_decorator
@attr.s
class TextElementStyle(object):
    bold = attr.ib(type=bool, default=None, metadata={'json': 'bold'})
    italic = attr.ib(type=bool, default=None, metadata={'json': 'italic'})
    strikethrough = attr.ib(type=bool, default=None, metadata={'json': 'strikethrough'})
    underline = attr.ib(type=bool, default=None, metadata={'json': 'underline'})
    inline_code = attr.ib(type=bool, default=None, metadata={'json': 'inline_code'})
    background_color = attr.ib(type=int, default=None, metadata={'json': 'background_color'})
    text_color = attr.ib(type=int, default=None, metadata={'json': 'text_color'})
    link = attr.ib(type=Link, default=None, metadata={'json': 'link'})


@to_json_decorator
@attr.s
class TextRun(object):
    content = attr.ib(type=str, default=None, metadata={'json': 'content'})
    text_element_style = attr.ib(type=TextElementStyle, default=None, metadata={'json': 'text_element_style'})


@to_json_decorator
@attr.s
class Isv(object):
    component_id = attr.ib(type=str, default=None, metadata={'json': 'component_id'})
    component_type_id = attr.ib(type=str, default=None, metadata={'json': 'component_type_id'})


@to_json_decorator
@attr.s
class InsertTableRowRequest(object):
    row_index = attr.ib(type=int, default=None, metadata={'json': 'row_index'})


@to_json_decorator
@attr.s
class InsertTableColumnRequest(object):
    column_index = attr.ib(type=int, default=None, metadata={'json': 'column_index'})


@to_json_decorator
@attr.s
class InsertGridColumnRequest(object):
    column_index = attr.ib(type=int, default=None, metadata={'json': 'column_index'})


@to_json_decorator
@attr.s
class InlineFile(object):
    file_token = attr.ib(type=str, default=None, metadata={'json': 'file_token'})
    source_block_id = attr.ib(type=str, default=None, metadata={'json': 'source_block_id'})


@to_json_decorator
@attr.s
class InlineBlock(object):
    block_id = attr.ib(type=str, default=None, metadata={'json': 'block_id'})


@to_json_decorator
@attr.s
class TextElement(object):
    text_run = attr.ib(type=TextRun, default=None, metadata={'json': 'text_run'})
    mention_user = attr.ib(type=MentionUser, default=None, metadata={'json': 'mention_user'})
    mention_doc = attr.ib(type=MentionDoc, default=None, metadata={'json': 'mention_doc'})
    reminder = attr.ib(type=Reminder, default=None, metadata={'json': 'reminder'})
    file = attr.ib(type=InlineFile, default=None, metadata={'json': 'file'})
    undefined = attr.ib(type=UndefinedElement, default=None, metadata={'json': 'undefined'})
    inline_block = attr.ib(type=InlineBlock, default=None, metadata={'json': 'inline_block'})


@to_json_decorator
@attr.s
class UpdateTextElementsRequest(object):
    elements = attr.ib(type=List[TextElement], default=None, metadata={'json': 'elements'})


@to_json_decorator
@attr.s
class Text(object):
    style = attr.ib(type=TextStyle, default=None, metadata={'json': 'style'})
    elements = attr.ib(type=List[TextElement], default=None, metadata={'json': 'elements'})


@to_json_decorator
@attr.s
class Image(object):
    width = attr.ib(type=int, default=None, metadata={'json': 'width'})
    height = attr.ib(type=int, default=None, metadata={'json': 'height'})
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})


@to_json_decorator
@attr.s
class IframeComponent(object):
    iframe_type = attr.ib(type=int, default=None, metadata={'json': 'iframe_type'})
    url = attr.ib(type=str, default=None, metadata={'json': 'url'})


@to_json_decorator
@attr.s
class Iframe(object):
    component = attr.ib(type=IframeComponent, default=None, metadata={'json': 'component'})


@to_json_decorator
@attr.s
class GridColumn(object):
    width_ratio = attr.ib(type=int, default=None, metadata={'json': 'width_ratio'})


@to_json_decorator
@attr.s
class Grid(object):
    column_size = attr.ib(type=int, default=None, metadata={'json': 'column_size'})


@to_json_decorator
@attr.s
class File(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})


@to_json_decorator
@attr.s
class Divider(object):
    pass


@to_json_decorator
@attr.s
class Diagram(object):
    diagram_type = attr.ib(type=int, default=None, metadata={'json': 'diagram_type'})


@to_json_decorator
@attr.s
class DeleteTableRowsRequest(object):
    row_start_index = attr.ib(type=int, default=None, metadata={'json': 'row_start_index'})
    row_end_index = attr.ib(type=int, default=None, metadata={'json': 'row_end_index'})


@to_json_decorator
@attr.s
class DeleteTableColumnsRequest(object):
    column_start_index = attr.ib(type=int, default=None, metadata={'json': 'column_start_index'})
    column_end_index = attr.ib(type=int, default=None, metadata={'json': 'column_end_index'})


@to_json_decorator
@attr.s
class DeleteGridColumnRequest(object):
    column_index = attr.ib(type=int, default=None, metadata={'json': 'column_index'})


@to_json_decorator
@attr.s
class UpdateBlockRequest(object):
    update_text_elements = attr.ib(type=UpdateTextElementsRequest, default=None, metadata={'json': 'update_text_elements'})
    update_text_style = attr.ib(type=UpdateTextStyleRequest, default=None, metadata={'json': 'update_text_style'})
    update_table_property = attr.ib(type=UpdateTablePropertyRequest, default=None, metadata={'json': 'update_table_property'})
    insert_table_row = attr.ib(type=InsertTableRowRequest, default=None, metadata={'json': 'insert_table_row'})
    insert_table_column = attr.ib(type=InsertTableColumnRequest, default=None, metadata={'json': 'insert_table_column'})
    delete_table_rows = attr.ib(type=DeleteTableRowsRequest, default=None, metadata={'json': 'delete_table_rows'})
    delete_table_columns = attr.ib(type=DeleteTableColumnsRequest, default=None, metadata={'json': 'delete_table_columns'})
    merge_table_cells = attr.ib(type=MergeTableCellsRequest, default=None, metadata={'json': 'merge_table_cells'})
    unmerge_table_cells = attr.ib(type=UnmergeTableCellsRequest, default=None, metadata={'json': 'unmerge_table_cells'})
    insert_grid_column = attr.ib(type=InsertGridColumnRequest, default=None, metadata={'json': 'insert_grid_column'})
    delete_grid_column = attr.ib(type=DeleteGridColumnRequest, default=None, metadata={'json': 'delete_grid_column'})
    update_grid_column_width_ratio = attr.ib(type=UpdateGridColumnWidthRatioRequest, default=None, metadata={'json': 'update_grid_column_width_ratio'})
    replace_image = attr.ib(type=ReplaceImageRequest, default=None, metadata={'json': 'replace_image'})
    replace_file = attr.ib(type=ReplaceFileRequest, default=None, metadata={'json': 'replace_file'})
    block_id = attr.ib(type=str, default=None, metadata={'json': 'block_id'})


@to_json_decorator
@attr.s
class ChatCard(object):
    __int_to_string_fields__ = attr.ib(type=List[str], default=["chat_id"])
    chat_id = attr.ib(type=int, default=None, metadata={'json': 'chat_id'})
    align = attr.ib(type=int, default=None, metadata={'json': 'align'})


@to_json_decorator
@attr.s
class Callout(object):
    background_color = attr.ib(type=int, default=None, metadata={'json': 'background_color'})
    border_color = attr.ib(type=int, default=None, metadata={'json': 'border_color'})
    text_color = attr.ib(type=int, default=None, metadata={'json': 'text_color'})
    emoji_id = attr.ib(type=str, default=None, metadata={'json': 'emoji_id'})


@to_json_decorator
@attr.s
class Bitable(object):
    token = attr.ib(type=str, default=None, metadata={'json': 'token'})
    view_type = attr.ib(type=int, default=None, metadata={'json': 'view_type'})


@to_json_decorator
@attr.s
class Block(object):
    block_id = attr.ib(type=str, default=None, metadata={'json': 'block_id'})
    parent_id = attr.ib(type=str, default=None, metadata={'json': 'parent_id'})
    children = attr.ib(type=List[str], default=None, metadata={'json': 'children'})
    block_type = attr.ib(type=int, default=None, metadata={'json': 'block_type'})
    page = attr.ib(type=Text, default=None, metadata={'json': 'page'})
    text = attr.ib(type=Text, default=None, metadata={'json': 'text'})
    heading1 = attr.ib(type=Text, default=None, metadata={'json': 'heading1'})
    heading2 = attr.ib(type=Text, default=None, metadata={'json': 'heading2'})
    heading3 = attr.ib(type=Text, default=None, metadata={'json': 'heading3'})
    heading4 = attr.ib(type=Text, default=None, metadata={'json': 'heading4'})
    heading5 = attr.ib(type=Text, default=None, metadata={'json': 'heading5'})
    heading6 = attr.ib(type=Text, default=None, metadata={'json': 'heading6'})
    heading7 = attr.ib(type=Text, default=None, metadata={'json': 'heading7'})
    heading8 = attr.ib(type=Text, default=None, metadata={'json': 'heading8'})
    heading9 = attr.ib(type=Text, default=None, metadata={'json': 'heading9'})
    bullet = attr.ib(type=Text, default=None, metadata={'json': 'bullet'})
    ordered = attr.ib(type=Text, default=None, metadata={'json': 'ordered'})
    code = attr.ib(type=Text, default=None, metadata={'json': 'code'})
    quote = attr.ib(type=Text, default=None, metadata={'json': 'quote'})
    equation = attr.ib(type=Text, default=None, metadata={'json': 'equation'})
    todo = attr.ib(type=Text, default=None, metadata={'json': 'todo'})
    bitable = attr.ib(type=Bitable, default=None, metadata={'json': 'bitable'})
    callout = attr.ib(type=Callout, default=None, metadata={'json': 'callout'})
    chat_card = attr.ib(type=ChatCard, default=None, metadata={'json': 'chat_card'})
    diagram = attr.ib(type=Diagram, default=None, metadata={'json': 'diagram'})
    divider = attr.ib(type=Divider, default=None, metadata={'json': 'divider'})
    file = attr.ib(type=File, default=None, metadata={'json': 'file'})
    grid = attr.ib(type=Grid, default=None, metadata={'json': 'grid'})
    grid_column = attr.ib(type=GridColumn, default=None, metadata={'json': 'grid_column'})
    iframe = attr.ib(type=Iframe, default=None, metadata={'json': 'iframe'})
    image = attr.ib(type=Image, default=None, metadata={'json': 'image'})
    isv = attr.ib(type=Isv, default=None, metadata={'json': 'isv'})
    mindnote = attr.ib(type=Mindnote, default=None, metadata={'json': 'mindnote'})
    sheet = attr.ib(type=Sheet, default=None, metadata={'json': 'sheet'})
    table = attr.ib(type=Table, default=None, metadata={'json': 'table'})
    table_cell = attr.ib(type=TableCell, default=None, metadata={'json': 'table_cell'})
    view = attr.ib(type=View, default=None, metadata={'json': 'view'})
    undefined = attr.ib(type=Undefined, default=None, metadata={'json': 'undefined'})


@to_json_decorator
@attr.s
class Document(object):
    document_id = attr.ib(type=str, default=None, metadata={'json': 'document_id'})
    revision_id = attr.ib(type=int, default=None, metadata={'json': 'revision_id'})
    title = attr.ib(type=str, default=None, metadata={'json': 'title'})



@to_json_decorator
@attr.s
class DocumentCreateReqBody(object):
    folder_token = attr.ib(type=str, default=None, metadata={'json': 'folder_token'})
    title = attr.ib(type=str, default=None, metadata={'json': 'title'})


@attr.s
class DocumentCreateResult(object):
    document = attr.ib(type=Document, default=None, metadata={'json': 'document'})



@attr.s
class DocumentGetResult(object):
    document = attr.ib(type=Document, default=None, metadata={'json': 'document'})



@attr.s
class DocumentRawContentResult(object):
    content = attr.ib(type=str, default=None, metadata={'json': 'content'})


@to_json_decorator
@attr.s
class DocumentBlockBatchUpdateReqBody(object):
    requests = attr.ib(type=List[UpdateBlockRequest], default=None, metadata={'json': 'requests'})


@attr.s
class DocumentBlockBatchUpdateResult(object):
    blocks = attr.ib(type=List[Block], default=None, metadata={'json': 'blocks'})
    document_revision_id = attr.ib(type=int, default=None, metadata={'json': 'document_revision_id'})
    client_token = attr.ib(type=str, default=None, metadata={'json': 'client_token'})



@attr.s
class DocumentBlockGetResult(object):
    block = attr.ib(type=Block, default=None, metadata={'json': 'block'})



@attr.s
class DocumentBlockListResult(object):
    items = attr.ib(type=List[Block], default=None, metadata={'json': 'items'})
    page_token = attr.ib(type=str, default=None, metadata={'json': 'page_token'})
    has_more = attr.ib(type=bool, default=None, metadata={'json': 'has_more'})



@attr.s
class DocumentBlockPatchResult(object):
    block = attr.ib(type=Block, default=None, metadata={'json': 'block'})
    document_revision_id = attr.ib(type=int, default=None, metadata={'json': 'document_revision_id'})
    client_token = attr.ib(type=str, default=None, metadata={'json': 'client_token'})


@to_json_decorator
@attr.s
class DocumentBlockChildrenBatchDeleteReqBody(object):
    start_index = attr.ib(type=int, default=None, metadata={'json': 'start_index'})
    end_index = attr.ib(type=int, default=None, metadata={'json': 'end_index'})


@attr.s
class DocumentBlockChildrenBatchDeleteResult(object):
    document_revision_id = attr.ib(type=int, default=None, metadata={'json': 'document_revision_id'})
    client_token = attr.ib(type=str, default=None, metadata={'json': 'client_token'})


@to_json_decorator
@attr.s
class DocumentBlockChildrenCreateReqBody(object):
    children = attr.ib(type=List[Block], default=None, metadata={'json': 'children'})
    index = attr.ib(type=int, default=None, metadata={'json': 'index'})


@attr.s
class DocumentBlockChildrenCreateResult(object):
    children = attr.ib(type=List[Block], default=None, metadata={'json': 'children'})
    document_revision_id = attr.ib(type=int, default=None, metadata={'json': 'document_revision_id'})
    client_token = attr.ib(type=str, default=None, metadata={'json': 'client_token'})



@attr.s
class DocumentBlockChildrenGetResult(object):
    items = attr.ib(type=List[Block], default=None, metadata={'json': 'items'})
    page_token = attr.ib(type=str, default=None, metadata={'json': 'page_token'})
    has_more = attr.ib(type=bool, default=None, metadata={'json': 'has_more'})