"""Converter: VideoChatContent → ``<meeting>...</meeting>`` block.

Aligned with node-sdk's ``converters/video-chat.ts``: emits a multi-line
``<meeting>`` block with 📹 topic + 🕙 start-time (if present), or the
fallback ``[video chat]`` placeholder.
"""

from typing import List, Tuple

from ...types import ResourceDescriptor, VideoChatContent
from ._utils import millis_to_datetime


def convert(content: VideoChatContent) -> Tuple[str, List[ResourceDescriptor]]:
    lines: List[str] = []
    if content.topic:
        lines.append(f"📹 {content.topic}")
    start = millis_to_datetime(content.start_time)
    if start:
        lines.append(f"🕙 {start}")
    inner = "\n".join(lines) if lines else "[video chat]"
    return f"<meeting>\n{inner}\n</meeting>", []
