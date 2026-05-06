"""Converter: UnknownContent / anything unrecognised → placeholder text."""

from typing import Any, List, Tuple

from ...types import ResourceDescriptor, UnknownContent


def convert(content: Any) -> Tuple[str, List[ResourceDescriptor]]:
    if isinstance(content, UnknownContent):
        raw = content.raw
        text = raw.get("text") if isinstance(raw, dict) else None
        return text or "[unsupported message]", []
    return "[unsupported message]", []
