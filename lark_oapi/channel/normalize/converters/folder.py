"""Converter: FolderContent → ``<folder key="..." name="..."/>``.

Aligned with node-sdk's ``converters/folder.ts``: ``key`` is the primary
identifier (the file_key on the wire), ``name`` is optional.

When ``file_key`` is missing, emits ``[folder]`` placeholder to match node.
"""

from typing import List, Tuple

from ...types import FolderContent, ResourceDescriptor
from ._utils import attr


def convert(content: FolderContent) -> Tuple[str, List[ResourceDescriptor]]:
    if not content.file_key:
        return "[folder]", []
    if content.file_name:
        return (
            f'<folder key="{content.file_key}" name="{attr(content.file_name)}"/>',
            [],
        )
    return f'<folder key="{content.file_key}"/>', []
