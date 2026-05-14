"""Converter: SystemContent → human-readable text via template expansion.

Lark system messages ship a template string with ``{var}`` placeholders
(e.g. ``"{from_user} invited {to_chatters}"``) plus a dict of values. We
expand the placeholders here so downstream consumers see
the rendered human text rather than the template.
"""

import re
from typing import List, Tuple

from ...types import ResourceDescriptor, SystemContent

_VAR_RE = re.compile(r"\{([a-z_]+)\}")


def convert(content: SystemContent) -> Tuple[str, List[ResourceDescriptor]]:
    template = content.template or ""
    if not template:
        return "[system message]", []

    raw = content.raw if isinstance(content.raw, dict) else {}

    def _replace(match: "re.Match[str]") -> str:
        name = match.group(1)
        val = raw.get(name)
        if isinstance(val, list):
            return ", ".join(_display(v) for v in val)
        if isinstance(val, str):
            return val
        if val is None:
            return ""
        return match.group(0)

    out = _VAR_RE.sub(_replace, template).strip()
    return out or "[system message]", []


def _display(v) -> str:
    """Best-effort stringify for a list element in a system message template.

    Lark ships from_user / to_chatters as lists of ``{id, name}`` dicts; we
    prefer the display name, then the id, then the raw repr.
    """
    if isinstance(v, dict):
        return v.get("name") or v.get("open_id") or v.get("id") or ""
    return str(v)
