"""Converter: StickerContent → ``<sticker .../>`` + resource."""

from typing import List, Tuple

from ...types import ResourceDescriptor, StickerContent


def convert(content: StickerContent) -> Tuple[str, List[ResourceDescriptor]]:
    key = content.file_key
    if not key:
        return "[sticker]", []
    return (
        f'<sticker key="{key}"/>',
        [ResourceDescriptor(type="sticker", file_key=key)],
    )
