"""Converter: TextContent → plain string."""

from typing import List, Tuple

from ...types import ResourceDescriptor, TextContent


def convert(content: TextContent) -> Tuple[str, List[ResourceDescriptor]]:
    return content.text, []
