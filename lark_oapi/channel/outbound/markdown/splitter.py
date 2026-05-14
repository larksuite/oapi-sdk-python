"""Code-fence-aware markdown splitter.

Aligned with node-sdk's ``channel/outbound/markdown/splitter.ts``. Splits a
markdown string into chunks at most ``limit`` chars while preserving fenced
code-block integrity across chunk boundaries.

Plain-text line chunking used by :class:`OutboundSender` lives next to the
sender itself (node-aligned — sender inlines chunking) and is not exposed
here.
"""

import re
from typing import List, Optional

_FENCE_RE = re.compile(r"^```(\w*)\s*$")
_HEADING_RE = re.compile(r"^#{1,6}\s")


def split_with_code_fences(text: str, limit: int) -> List[str]:
    """Markdown-aware splitter.

    Guarantees:
        - Each returned chunk is <= ``limit`` chars (bar a rare hard-overflow
          when a single line exceeds the limit).
        - Splits inside a fenced code block close with ``` and the next chunk
          reopens with the same language tag.
        - Prefers to break just *before* a heading line when the current
          buffer is already ~75% full, so headings lead their chunk.
    """
    if len(text) <= limit:
        return [text]
    lines = text.split("\n")
    out: List[str] = []
    buf: List[str] = []
    buf_len = 0
    fence_lang: Optional[str] = None  # None when outside a fence

    def flush():
        nonlocal buf, buf_len
        if not buf:
            return
        chunk = "\n".join(buf)
        if fence_lang is not None:
            chunk += "\n```"
        out.append(chunk)
        buf = []
        buf_len = 0
        if fence_lang is not None:
            reopen = "```" + fence_lang
            buf.append(reopen)
            buf_len = len(reopen)

    for line in lines:
        m = _FENCE_RE.match(line)
        line_len = len(line) + (1 if buf else 0)
        is_heading = bool(_HEADING_RE.match(line))
        near_full = buf_len > limit * 0.75

        if buf_len + line_len > limit or (is_heading and near_full and buf):
            flush()

        buf.append(line)
        buf_len += line_len
        if m:
            fence_lang = (m.group(1) or "") if fence_lang is None else None

    flush()
    return out
