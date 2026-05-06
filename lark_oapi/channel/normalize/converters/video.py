"""Converter: MediaContent (video) → ``<video .../>`` + resource."""

from typing import List, Tuple

from ...types import MediaContent, ResourceDescriptor
from ._utils import attr, format_duration


def convert(content: MediaContent) -> Tuple[str, List[ResourceDescriptor]]:
    key = content.file_key
    cover = content.image_key
    dur = format_duration(content.duration_ms)
    name = content.file_name or ""
    if not key:
        return "[video]", []
    return (
        f'<video key="{key}" name="{attr(name)}" duration="{dur}"/>',
        [
            ResourceDescriptor(
                type="video",
                file_key=key,
                file_name=content.file_name,
                duration_ms=content.duration_ms,
                cover_image_key=cover,
            )
        ],
    )
