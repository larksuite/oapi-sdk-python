"""Parse Lark mention placeholders (node-aligned API).

Mirrors node-sdk's ``channel/normalize/mentions.ts`` two-step flow:

    ext = extract_mentions(raw, bot_open_id)   # parse + index
    text = resolve_mentions(text, ext)         # second-pass replace

:func:`is_mention_all` matches node's ``isMentionAll`` (detects by key
``@_all`` or ``id.user_id == "all"``).

``parse_at_tags`` is a Python-only helper for post / card payloads that
inline ``<at user_id="...">Name</at>`` tags — node handles these inside its
converter walk, so there's no direct counterpart.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..types import Mention

_PLACEHOLDER_RE = re.compile(r"@_user_\d+")
# Matches the ``@_all`` mention-all placeholder Feishu embeds in text content
# for messages that mention everyone. Needs a non-word-char (or
# end-of-string) boundary after ``@_all`` so we don't misfire on, say,
# ``@_all_employees``.
_AT_ALL_RE = re.compile(r"@_all(?![A-Za-z0-9_])")

# Human-visible string substituted in place of the ``@_all`` placeholder
# when resolving mentions. ``@all`` is the locale-neutral default; callers
# wanting a localized rendering can monkey-patch this module attribute.
MENTION_ALL_DISPLAY = "@all"
_AT_TAG_RE = re.compile(
    r"<at\s+([^>]*?)>(?P<name>.*?)</at>",
    re.IGNORECASE | re.DOTALL,
)
_ATTR_RE = re.compile(r'([\w_-]+)\s*=\s*"([^"]*)"')


def text_has_mention_all(text: Optional[str]) -> bool:
    """True if ``text`` contains the ``@_all`` placeholder.

    Feishu does NOT populate ``event.message.mentions`` for mention-all
    messages in all cases — the only signal can be an ``@_all`` token
    inside ``content.text``. Without detecting that, downstream policy
    code sees ``mentioned_all=False`` and the ``mention_all_blocked``
    gate never fires.
    """
    if not text:
        return False
    return _AT_ALL_RE.search(text) is not None


# ---------------------------------------------------------------------------
# Data shape
# ---------------------------------------------------------------------------


@dataclass
class MentionExtraction:
    """Indexed result of :func:`extract_mentions`.

    Mirrors node's ``MentionExtraction`` interface.
    """

    mentions: Dict[str, Mention] = field(default_factory=dict)
    """Keyed by placeholder (e.g. ``@_user_1``)."""

    mentions_by_open_id: Dict[str, Mention] = field(default_factory=dict)
    """Keyed by ``open_id`` (excludes @all)."""

    mention_list: List[Mention] = field(default_factory=list)
    """Filtered list: no @all, no bot self-mention."""

    mentioned_all: bool = False
    mentioned_bot: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def is_mention_all(m: Any) -> bool:
    """True if ``m`` represents an ``@all`` mention (node-aligned)."""
    if isinstance(m, dict):
        if m.get("key") == "@_all":
            return True
        ident = m.get("id")
        if isinstance(ident, dict) and ident.get("user_id") == "all":
            return True
        return False
    if getattr(m, "key", None) == "@_all":
        return True
    ident = getattr(m, "id", None)
    return ident is not None and getattr(ident, "user_id", None) == "all"


def _mention_from_event(m: Any) -> Mention:
    if isinstance(m, dict):
        ident = m.get("id") if isinstance(m.get("id"), dict) else {}
        return Mention(
            key=m.get("key") or "",
            open_id=ident.get("open_id") if ident else None,
            union_id=ident.get("union_id") if ident else None,
            user_id=ident.get("user_id") if ident else None,
            name=m.get("name"),
            tenant_key=m.get("tenant_key"),
        )
    ident = getattr(m, "id", None)
    return Mention(
        key=getattr(m, "key", "") or "",
        open_id=getattr(ident, "open_id", None) if ident is not None else None,
        union_id=getattr(ident, "union_id", None) if ident is not None else None,
        user_id=getattr(ident, "user_id", None) if ident is not None else None,
        name=getattr(m, "name", None),
        tenant_key=getattr(m, "tenant_key", None),
    )


# ---------------------------------------------------------------------------
# Public API (node-aligned)
# ---------------------------------------------------------------------------


def extract_mentions(
        raw: Optional[Iterable[Any]],
        bot_open_id: Optional[str] = None,
) -> MentionExtraction:
    """Index raw event mentions into a :class:`MentionExtraction`.

    - ``@all`` entries set ``mentioned_all`` and are excluded from lists.
    - Entries whose ``open_id`` matches ``bot_open_id`` set ``mentioned_bot``
      and are also excluded from ``mention_list`` (but kept in ``mentions``
      by key so :func:`resolve_mentions` can still strip placeholders).
    """
    out = MentionExtraction()
    for m in (raw or []):
        if is_mention_all(m):
            out.mentioned_all = True
            continue
        parsed = _mention_from_event(m)
        if parsed.key:
            out.mentions[parsed.key] = parsed
        if parsed.open_id:
            out.mentions_by_open_id[parsed.open_id] = parsed
        if bot_open_id and parsed.open_id == bot_open_id:
            out.mentioned_bot = True
            continue
        out.mention_list.append(parsed)
    return out


def resolve_mentions(
        content: str,
        ext: MentionExtraction,
        *,
        strip_bot_mentions: bool = False,
        bot_open_id: Optional[str] = None,
) -> str:
    """Replace ``@_user_N`` placeholders with ``@{name}``.

    When ``strip_bot_mentions=True`` and ``bot_open_id`` is provided,
    placeholders referencing the bot are removed outright (adjacent
    whitespace normalized).
    """
    if not content:
        return content or ""

    def _replace(match: "re.Match[str]") -> str:
        key = match.group(0)
        m = ext.mentions.get(key)
        if m is None:
            return key
        if strip_bot_mentions and bot_open_id and m.open_id == bot_open_id:
            return ""
        if not m.name:
            return key
        return f"@{m.name}"

    result = _PLACEHOLDER_RE.sub(_replace, content)
    # Rewrite ``@_all`` placeholder to the human-visible form; without this
    # user-visible content carries the raw token.
    result = _AT_ALL_RE.sub(MENTION_ALL_DISPLAY, result)
    if strip_bot_mentions:
        result = re.sub(r"\s{2,}", " ", result).strip()
    return result


# ---------------------------------------------------------------------------
# Python-only helper: inline <at> tags inside post / card rendered content
# ---------------------------------------------------------------------------


def parse_at_tags(text: str) -> Tuple[List[Mention], bool, str]:
    """Strip ``<at user_id="ou_xxx">Name</at>`` tags into mentions + text.

    Used for post / card rendered payloads where placeholders are unavailable.
    No direct node counterpart — node handles this inside per-converter walks.
    """
    mentions: List[Mention] = []
    mentioned_all = False

    def _replace(match: "re.Match[str]") -> str:
        nonlocal mentioned_all
        attrs = dict(_ATTR_RE.findall(match.group(1)))
        uid = attrs.get("user_id") or attrs.get("open_id") or ""
        name = match.group("name") or attrs.get("user_name") or ""
        if uid == "all":
            mentioned_all = True
            return MENTION_ALL_DISPLAY
        mentions.append(
            Mention(
                key=f"@_at_{uid}",
                open_id=uid if uid.startswith("ou_") else None,
                user_id=uid if not uid.startswith("ou_") else None,
                name=name or None,
            )
        )
        return f"@{name}" if name else f"@{uid}"

    stripped = _AT_TAG_RE.sub(_replace, text)
    return mentions, mentioned_all, stripped
