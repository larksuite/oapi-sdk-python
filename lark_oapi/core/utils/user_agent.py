"""User-Agent construction.

Mirrors node-sdk's `buildUserAgent`: returns the base SDK token, optionally
appends a sanitized ``source/<name>`` product token, and finally appends any
sub-module supplied bare tokens (e.g. ``channel``).
"""

import re
from typing import Iterable, Optional

from lark_oapi.core.const import PROJECT, VERSION

_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9._-]")


def sanitize_source(raw: str) -> str:
    """Replace non-token characters with ``_`` and clamp length to 64.

    Returns an empty string when ``raw`` is falsy or sanitizes to nothing.
    """
    if not raw:
        return ""
    return _SANITIZE_RE.sub("_", raw)[:64]


def build_user_agent(
        source: Optional[str] = None,
        extra_tags: Optional[Iterable[str]] = None,
) -> str:
    """Build the User-Agent string.

    Format::

        oapi-sdk-python/v<version>[ source/<sanitized>][ <tag>...]

    ``extra_tags`` is internal — sub-modules (e.g. channel) use it to mark
    requests they originate.
    """
    ua = f"{PROJECT}/v{VERSION}"
    if source:
        clean = sanitize_source(source)
        if clean:
            ua += f" source/{clean}"
    if extra_tags:
        for tag in extra_tags:
            clean = sanitize_source(tag)
            if clean:
                ua += f" {clean}"
    return ua
