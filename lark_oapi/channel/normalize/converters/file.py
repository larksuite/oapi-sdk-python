"""Converter: FileContent → ``<file .../>`` + resource."""

from typing import List, Tuple

from ...types import FileContent, ResourceDescriptor
from ._utils import attr


def convert(content: FileContent) -> Tuple[str, List[ResourceDescriptor]]:
    key = content.file_key
    name = content.file_name or ""
    if not key:
        return "[file]", []
    return (
        f'<file key="{key}" name="{attr(name)}"/>',
        [ResourceDescriptor(type="file", file_key=key, file_name=content.file_name)],
    )
