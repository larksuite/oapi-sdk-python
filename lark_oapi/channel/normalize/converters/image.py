"""Converter: ImageContent → ``![image](image_key)`` + resource."""

from typing import List, Tuple

from ...types import ImageContent, ResourceDescriptor


def convert(content: ImageContent) -> Tuple[str, List[ResourceDescriptor]]:
    key = content.image_key
    if not key:
        return "[image]", []
    return f"![image]({key})", [ResourceDescriptor(type="image", file_key=key)]
