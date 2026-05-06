"""Flatten a :class:`MessageContent` union into ``(content_text, resources)``.

Dispatches to per-type converters in :mod:`.converters`. Layout mirrors
node-sdk's ``channel/normalize/converters/*.ts`` + ``registry.ts`` pair; new
message types are added by dropping a file into ``converters/`` and
registering it in ``converters/__init__.py`` — no changes here.
"""

from typing import List, Tuple

from ..types import MessageContent, ResourceDescriptor
from .converters import REGISTRY, fallback


def flatten(content: MessageContent) -> Tuple[str, List[ResourceDescriptor]]:
    """Return ``(content_text, resources)`` for a ``MessageContent`` variant."""
    converter = REGISTRY.get(type(content))
    if converter is not None:
        return converter(content)
    return fallback.convert(content)
