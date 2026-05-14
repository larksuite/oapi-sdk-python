"""Converter: VoteContent → ``<vote>...</vote>`` block.

Aligned with node-sdk's ``converters/vote.ts``: emits the topic on its own
line, then each option prefixed with ``• `` (bullet), wrapped in ``<vote>``.
"""

from typing import List, Tuple

from ...types import ResourceDescriptor, VoteContent


def convert(content: VoteContent) -> Tuple[str, List[ResourceDescriptor]]:
    if not content.topic and not content.options:
        return "<vote>\n[vote]\n</vote>", []
    lines: List[str] = []
    if content.topic:
        lines.append(content.topic)
    for opt in content.options or []:
        lines.append(f"• {opt}")
    return "<vote>\n" + "\n".join(lines) + "\n</vote>", []
