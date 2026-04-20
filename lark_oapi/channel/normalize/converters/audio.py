"""Converter: AudioContent → ``<audio .../>`` + resource."""

from typing import List, Tuple

from ...types import AudioContent, ResourceDescriptor
from ._utils import format_duration


def convert(content: AudioContent) -> Tuple[str, List[ResourceDescriptor]]:
    key = content.file_key
    dur = format_duration(content.duration_ms)
    if not key:
        return "[audio]", []
    return (
        f'<audio key="{key}" duration="{dur}"/>',
        [ResourceDescriptor(type="audio", file_key=key, duration_ms=content.duration_ms)],
    )
