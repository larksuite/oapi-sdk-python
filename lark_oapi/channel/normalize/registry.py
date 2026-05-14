"""Convert Lark EventMessage.content JSON into a MessageContent variant.

The Lark platform currently supports 19 message types. We produce a uniform
`MessageContent` union so callers do not need to switch on the original
wire schema.

This module handles the SYNCHRONOUS parsing step only — async expansion
(merge_forward child fetch, interactive card re-fetch) is layered on top in
`pipeline.py`.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from lark_oapi.core.log import logger

from ..types import (
    AudioContent,
    CalendarContent,
    FileContent,
    FolderContent,
    GeneralCalendarContent,
    HongbaoContent,
    ImageContent,
    InteractiveContent,
    LocationContent,
    MediaContent,
    MergeForwardContent,
    MessageContent,
    PostContent,
    ShareCalendarEventContent,
    ShareChatContent,
    ShareUserContent,
    StickerContent,
    SystemContent,
    TextContent,
    TodoContent,
    UnknownContent,
    VideoChatContent,
    VoteContent,
)


def _safe_json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    if isinstance(raw, str) and raw:
        try:
            decoded = json.loads(raw)
            if isinstance(decoded, dict):
                return decoded
        except (ValueError, TypeError) as e:  # pragma: no cover - defensive
            logger.debug("parse_message_content: invalid JSON content: %s", e)
    return {}


def _flatten_post_text(post: Dict[str, Any]) -> Tuple[str, str]:
    """Return (title, plain_text) from a post AST.

    Post content has locale keys (`zh_cn`, `en_us`). We pick the first locale.
    """
    if not isinstance(post, dict):
        return "", ""
    first_key = next(iter(post), None)
    if first_key is None:
        return "", ""
    locale_doc = post.get(first_key)
    if not isinstance(locale_doc, dict):
        return "", ""
    title = locale_doc.get("title") or ""
    lines: List[str] = []
    for para in locale_doc.get("content") or []:
        chunk: List[str] = []
        for el in para or []:
            if not isinstance(el, dict):
                continue
            tag = el.get("tag")
            if tag == "text":
                chunk.append(el.get("text") or "")
            elif tag == "a":
                chunk.append(el.get("text") or el.get("href") or "")
            elif tag == "at":
                nm = el.get("user_name") or el.get("user_id") or ""
                chunk.append(f"@{nm}" if nm else "@")
            elif tag == "emotion":
                chunk.append(f":{el.get('emoji_type') or ''}:")
            elif tag == "img":
                chunk.append("[image]")
            elif tag == "media":
                chunk.append("[media]")
            elif tag == "code_block":
                chunk.append(el.get("text") or "")
            elif tag == "hr":
                chunk.append("---")
            elif tag == "md":
                chunk.append(el.get("text") or "")
        lines.append("".join(chunk))
    return title, "\n".join(lines)


def _parse_text(data: Dict[str, Any]) -> TextContent:
    return TextContent(text=data.get("text") or "", raw=data)


def _parse_post(data: Dict[str, Any]) -> PostContent:
    title, text = _flatten_post_text(data)
    return PostContent(title=title, text=text, post=data, raw=data)


def _parse_image(data: Dict[str, Any]) -> ImageContent:
    return ImageContent(image_key=data.get("image_key") or "", raw=data)


def _parse_file(data: Dict[str, Any]) -> FileContent:
    return FileContent(
        file_key=data.get("file_key") or "",
        file_name=data.get("file_name"),
        raw=data,
    )


def _parse_audio(data: Dict[str, Any]) -> AudioContent:
    return AudioContent(
        file_key=data.get("file_key") or "",
        duration_ms=data.get("duration"),
        raw=data,
    )


def _parse_media(data: Dict[str, Any]) -> MediaContent:
    return MediaContent(
        file_key=data.get("file_key") or "",
        image_key=data.get("image_key"),
        duration_ms=data.get("duration"),
        file_name=data.get("file_name"),
        raw=data,
    )


def _parse_sticker(data: Dict[str, Any]) -> StickerContent:
    return StickerContent(file_key=data.get("file_key") or "", raw=data)


def _parse_interactive(data: Dict[str, Any]) -> InteractiveContent:
    """Build a minimal InteractiveContent from the event payload.

    The event payload only contains truncated metadata — the pipeline will
    decide whether to re-fetch the full card JSON via the API.
    """
    version = "unknown"
    if isinstance(data, dict):
        if "schema" in data or "header" in data or "body" in data:
            version = "v2"
        elif "card" in data or "config" in data or "elements" in data:
            version = "v1"
    return InteractiveContent(card=data, card_version=version, raw=data)


def _parse_share_chat(data: Dict[str, Any]) -> ShareChatContent:
    return ShareChatContent(chat_id=data.get("chat_id") or "", raw=data)


def _parse_share_user(data: Dict[str, Any]) -> ShareUserContent:
    return ShareUserContent(user_id=data.get("user_id") or "", raw=data)


def _parse_system(data: Dict[str, Any]) -> SystemContent:
    return SystemContent(
        template=data.get("template") or "",
        from_user=data.get("from_user") or [],
        to_chatters=data.get("to_chatters") or [],
        raw=data,
    )


def _parse_location(data: Dict[str, Any]) -> LocationContent:
    def _f(v: Any) -> Optional[float]:
        try:
            return float(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    return LocationContent(
        name=data.get("name") or "",
        longitude=_f(data.get("longitude")),
        latitude=_f(data.get("latitude")),
        raw=data,
    )


def _parse_video_chat(data: Dict[str, Any]) -> VideoChatContent:
    return VideoChatContent(
        topic=data.get("topic") or "",
        start_time=data.get("start_time"),
        raw=data,
    )


def _parse_calendar(data: Dict[str, Any]) -> CalendarContent:
    return CalendarContent(
        summary=data.get("summary") or "",
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        raw=data,
    )


def _parse_vote(data: Dict[str, Any]) -> VoteContent:
    return VoteContent(
        topic=data.get("topic") or "",
        options=list(data.get("options") or []),
        raw=data,
    )


def _parse_todo(data: Dict[str, Any]) -> TodoContent:
    """Todo's ``summary`` on the wire is ``{title, content: PostElement[][]}``.

    We lift ``title`` + flat body text so downstream converters don't need to
    re-walk the AST. Falls back to treating ``summary`` as a plain string if
    the platform ever ships that shape.
    """
    summary = data.get("summary")
    title = ""
    body = ""
    if isinstance(summary, dict):
        title = summary.get("title") or ""
        body = _extract_post_plain_text(summary.get("content"))
    elif isinstance(summary, str):
        title = summary
    return TodoContent(
        title=title,
        body=body,
        due_time=data.get("due_time"),
        raw=data,
    )


def _extract_post_plain_text(blocks: Any) -> str:
    """Flatten a post-AST ``PostElement[][]`` into plain text.

    Mirrors node-sdk's ``extractPostPlainText``: keeps only ``text`` / ``a``
    element text, joins elements within a paragraph with empty string, joins
    paragraphs with newline.
    """
    if not isinstance(blocks, list):
        return ""
    lines: List[str] = []
    for para in blocks:
        if not isinstance(para, list):
            continue
        parts: List[str] = []
        for el in para:
            if not isinstance(el, dict):
                continue
            tag = el.get("tag")
            text = el.get("text")
            if tag in ("text", "a") and text:
                parts.append(text)
        if parts:
            lines.append("".join(parts))
    return "\n".join(lines)


def _parse_merge_forward(data: Dict[str, Any]) -> MergeForwardContent:
    """Build a loading=True merge_forward; pipeline is responsible for expansion."""
    return MergeForwardContent(loading=True, raw=data)


def _parse_folder(data: Dict[str, Any]) -> FolderContent:
    return FolderContent(
        file_key=data.get("file_key") or "",
        file_name=data.get("file_name") or data.get("name") or "",
        file_size=data.get("file_size"),
        raw=data,
    )


def _parse_hongbao(data: Dict[str, Any]) -> HongbaoContent:
    amount = data.get("amount")
    try:
        amount = int(amount) if amount is not None else None
    except (TypeError, ValueError):
        amount = None
    return HongbaoContent(
        text=data.get("text") or data.get("title") or "",
        amount=amount,
        raw=data,
    )


def _parse_general_calendar(data: Dict[str, Any]) -> GeneralCalendarContent:
    return GeneralCalendarContent(
        summary=data.get("summary") or data.get("title") or "",
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        raw=data,
    )


def _parse_share_calendar_event(data: Dict[str, Any]) -> ShareCalendarEventContent:
    return ShareCalendarEventContent(
        summary=data.get("summary") or "",
        organizer=data.get("organizer_display_name") or data.get("organizer") or "",
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        raw=data,
    )


_PARSERS = {
    "text": _parse_text,
    "post": _parse_post,
    "image": _parse_image,
    "file": _parse_file,
    "audio": _parse_audio,
    # `media` and `video` share the same parser; the richer `MediaContent`
    # dataclass carries the extra fields when they are present on the wire.
    "media": _parse_media,
    "video": _parse_media,
    "sticker": _parse_sticker,
    "interactive": _parse_interactive,
    "share_chat": _parse_share_chat,
    "share_user": _parse_share_user,
    "system": _parse_system,
    "location": _parse_location,
    "folder": _parse_folder,
    "hongbao": _parse_hongbao,
    "video_chat": _parse_video_chat,
    "calendar": _parse_calendar,
    "general_calendar": _parse_general_calendar,
    "share_calendar_event": _parse_share_calendar_event,
    "vote": _parse_vote,
    "todo": _parse_todo,
    "merge_forward": _parse_merge_forward,
}


def parse_message_content(message_type: str, raw_content: Any) -> MessageContent:
    """Synchronous first-pass parse.

    - `message_type` drives the dispatch.
    - `raw_content` is the string or dict from EventMessage.content.
    - Unknown types fall back to `UnknownContent` — never raises.
    """
    data = _safe_json(raw_content)
    parser = _PARSERS.get(message_type or "")
    if parser is None:
        return UnknownContent(message_type=message_type or "", raw=data)
    try:
        return parser(data)
    except Exception as e:  # pragma: no cover - defensive
        logger.exception("parse_message_content failed for %s: %s", message_type, e)
        return UnknownContent(message_type=message_type or "", raw=data)


SUPPORTED_MESSAGE_TYPES: Tuple[str, ...] = tuple(_PARSERS.keys())
