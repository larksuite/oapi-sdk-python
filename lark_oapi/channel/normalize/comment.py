"""Normalize ``drive.notice.comment_add_v1`` events.

Wire payload (verified against the live Feishu tenant API)::

    {
      "file_token": "...",
      "file_type": "docx",
      "comment_id": "...",
      "reply_id": "...",
      "is_mentioned": true,
      "create_time": "1700000000000",   # ms, string
      "notice_meta": {
        "from_user_id":  { "open_id": "...", "user_id": "...", "union_id": "..." },
        "to_user_id":    { ... },
        "file_token": "...",
        "file_type": "docx",
        "timestamp": "1700000000000",
        "is_mentioned": true,
        "notice_type": "comment_add"
      },
      // Legacy fallbacks (older p1 callbacks):
      "user_id":   { "open_id": "...", ... },
      "is_mention": true,
      "action_time": "1700000000000"
    }

The operator lives at ``notice_meta.from_user_id`` (top-level
``user_id`` is the legacy fallback). Whether the bot was mentioned is a
boolean flag (``is_mentioned``), not a probe of the mentions array.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CommentOperator:
    open_id: Optional[str] = None
    user_id: Optional[str] = None
    union_id: Optional[str] = None


@dataclass
class CommentEvent:
    file_token: str
    file_type: str
    comment_id: str
    reply_id: Optional[str]
    operator: CommentOperator
    mentioned_bot: bool
    timestamp: int
    raw: Dict[str, Any] = field(default_factory=dict)


def normalize_comment(
        data: Any,
        *,
        bot_open_id: Optional[str] = None,
        envelope_timestamp: Optional[str] = None,
) -> Optional[CommentEvent]:
    """Flatten the raw ``drive.notice.comment_add_v1`` payload.

    Accepts either the whole envelope (with ``event`` key) or the inner
    event dict. Returns ``None`` when the payload is malformed or missing
    one of the required fields (``file_token`` / ``file_type`` /
    ``comment_id`` / operator open_id).

    ``envelope_timestamp`` is the ``header.create_time`` (p2) or top-level
    ``ts`` (p1) carried by the WS/HTTP envelope. The inner event payload
    omits a per-event timestamp on the wire, so the envelope is the only
    reliable source — pass it from the dispatcher callback.

    ``bot_open_id`` is unused — the bot-mention signal is sourced from the
    payload's ``is_mentioned`` flag instead. The parameter is kept for
    backward compatibility with the previous (broken) implementation.
    """
    if not isinstance(data, dict):
        data = _try_dict(data)
        if data is None:
            return None
    event = data.get("event") if isinstance(data.get("event"), dict) else data
    if not isinstance(event, dict):
        return None
    notice_meta = event.get("notice_meta") if isinstance(event.get("notice_meta"), dict) else {}

    file_token = event.get("file_token") or notice_meta.get("file_token") or ""
    file_type = event.get("file_type") or notice_meta.get("file_type") or ""
    comment_id = event.get("comment_id") or notice_meta.get("comment_id") or ""

    # Operator: prefer notice_meta.from_user_id (current p2 wire format),
    # fall back to top-level user_id (legacy p1 callback shape). The old
    # path looked at ``event.operator`` / ``event.operator_id`` — neither
    # is in the actual payload, so operator came back null.
    user_id_obj = notice_meta.get("from_user_id") or event.get("user_id") or {}
    if not isinstance(user_id_obj, dict):
        user_id_obj = {}
    operator_open_id = user_id_obj.get("open_id")

    # Required-field gate (node-aligned). Missing operator open_id is a
    # malformed payload — drop rather than deliver a half-populated event.
    if not (file_token and file_type and comment_id and operator_open_id):
        return None

    reply_id = event.get("reply_id") or notice_meta.get("reply_id") or None

    op = CommentOperator(
        open_id=operator_open_id,
        user_id=user_id_obj.get("user_id"),
        union_id=user_id_obj.get("union_id"),
    )

    mentioned_bot_flag = bool(
        event.get("is_mentioned")
        if event.get("is_mentioned") is not None
        else (notice_meta.get("is_mentioned") or event.get("is_mention"))
    )

    ts_str = (
            event.get("create_time")
            or notice_meta.get("timestamp")
            or event.get("action_time")
            or event.get("event_create_time")
            or event.get("timestamp")
            or envelope_timestamp
    )
    try:
        ts = int(ts_str) if ts_str is not None else 0
    except (TypeError, ValueError):
        ts = 0

    return CommentEvent(
        file_token=file_token,
        file_type=file_type,
        comment_id=comment_id,
        reply_id=reply_id,
        operator=op,
        mentioned_bot=mentioned_bot_flag,
        timestamp=ts,
        raw=event,
    )


def _try_dict(obj) -> Optional[Dict[str, Any]]:
    try:
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_")}
    except Exception:  # pragma: no cover
        return None
