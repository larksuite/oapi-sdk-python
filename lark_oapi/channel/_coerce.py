"""Input coercion helpers shared by :class:`FeishuChannel`.

**Internal module — do not import from outside ``lark_oapi.channel``.** The
leading underscore in the module name is Python's convention for "package
private". Names, signatures, and behaviour here are free to change between
minor versions without deprecation warnings. ``FeishuChannel.send`` /
``.stream`` etc. are the public surface; use them instead of ``coerce_*``
helpers directly.

These turn node-style dict / string / dataclass inputs into the internal
:class:`OutboundMessage` / :class:`MediaSource` / :class:`SendOpts` shapes the
sender expects. Extracted from :mod:`.channel` to keep the main class focused.
"""

import inspect
import json
from typing import Any, Dict, Optional, Union

from lark_oapi.core.json import JSON

from .errors import FeishuChannelErrorCode, SendError
from .types import (
    MediaSource,
    OutboundAudio,
    OutboundCard,
    OutboundFile,
    OutboundImage,
    OutboundMessage,
    OutboundPost,
    OutboundShareChat,
    OutboundShareUser,
    OutboundSticker,
    OutboundText,
    OutboundVideo,
    SendOpts,
    SendResult,
)

# --------------------------------------------------------------------------
# Event-name normalization (node-aligned)
# --------------------------------------------------------------------------

VALID_EVENTS = {
    "message",
    "interaction", "cardAction", "card_action",
    "reaction",
    "bot_added", "botAdded",
    "bot_left", "botLeave", "bot_leave",
    "message_read", "messageRead",
    "reject",
    "comment",
    "raw", "raw_event",
    "reconnecting",
    "reconnected",
    "error",
}

_EVENT_ALIASES = {
    "card_action": "cardAction",
    "interaction": "cardAction",
    "bot_added": "botAdded",
    "bot_join": "botAdded",
    "bot_left": "botLeave",
    "bot_leave": "botLeave",
    "message_read": "messageRead",
    "raw_event": "raw",
}


def normalize_event_name(name: str) -> str:
    return _EVENT_ALIASES.get(name, name)


# --------------------------------------------------------------------------
# Input coercion
# --------------------------------------------------------------------------


def coerce_outbound(
        input_: Union[Dict[str, Any], OutboundMessage, str],
) -> OutboundMessage:
    if isinstance(input_, str):
        return OutboundPost(markdown=input_)
    if isinstance(
            input_,
            (
                    OutboundText, OutboundPost, OutboundCard, OutboundImage,
                    OutboundFile, OutboundAudio, OutboundVideo,
                    OutboundShareChat, OutboundShareUser, OutboundSticker,
            ),
    ):
        return input_
    if not isinstance(input_, dict):
        raise TypeError(f"Unsupported send input: {type(input_).__name__}")

    if "markdown" in input_:
        return OutboundPost(markdown=input_["markdown"])
    if "text" in input_:
        return OutboundText(text=input_["text"])
    if "post" in input_:
        return OutboundPost(post=input_["post"])
    if "card" in input_:
        return OutboundCard(card=input_["card"])
    if "image" in input_:
        return OutboundImage(
            source=coerce_media_source(input_["image"], kind="image"),
            caption=_coerce_caption(input_.get("caption")),
        )
    if "file" in input_:
        return OutboundFile(
            source=coerce_media_source(input_["file"], kind="file"),
            file_name=_dict_get_any(input_["file"], ("fileName", "file_name")),
            caption=_coerce_caption(input_.get("caption")),
        )
    if "audio" in input_:
        return OutboundAudio(
            source=coerce_media_source(input_["audio"], kind="audio"),
            caption=_coerce_caption(input_.get("caption")),
        )
    if "video" in input_:
        return OutboundVideo(
            source=coerce_media_source(input_["video"], kind="video"),
            caption=_coerce_caption(input_.get("caption")),
        )
    if "share_chat" in input_ or "shareChat" in input_:
        spec = input_.get("share_chat") or input_.get("shareChat") or {}
        chat_id = spec if isinstance(spec, str) else _dict_get_any(
            spec, ("chat_id", "chatId")
        )
        if not chat_id:
            raise TypeError("share_chat requires a chat_id (str or {chat_id: ...})")
        return OutboundShareChat(chat_id=chat_id)
    if "share_user" in input_ or "shareUser" in input_:
        spec = input_.get("share_user") or input_.get("shareUser") or {}
        user_id = spec if isinstance(spec, str) else _dict_get_any(
            spec, ("user_id", "userId", "open_id", "openId")
        )
        if not user_id:
            raise TypeError("share_user requires a user_id (str or {user_id: ...})")
        return OutboundShareUser(user_id=user_id)
    if "sticker" in input_:
        spec = input_["sticker"]
        file_key = spec if isinstance(spec, str) else _dict_get_any(
            spec, ("file_key", "fileKey")
        )
        if not file_key:
            raise TypeError("sticker requires a file_key (str or {file_key: ...})")
        return OutboundSticker(file_key=file_key)
    raise TypeError(f"send: unrecognized input keys {list(input_.keys())}")


def coerce_media_source(spec: Any, *, kind: str) -> MediaSource:
    if isinstance(spec, MediaSource):
        return spec
    if isinstance(spec, bytes):
        return MediaSource(kind="buffer", buffer=spec)
    if not isinstance(spec, dict):
        raise TypeError(f"{kind} input must be a dict or MediaSource")
    src = spec.get("source")
    if isinstance(src, MediaSource):
        return src
    if isinstance(src, bytes):
        return MediaSource(kind="buffer", buffer=src)
    if isinstance(src, str):
        if src.startswith(("http://", "https://")):
            return MediaSource(kind="url", url=src)
        if src.startswith(("img_", "file_", "st_")):
            return MediaSource(kind="key", key=src)
        return MediaSource(kind="file", path=src)
    raise TypeError(f"{kind}.source must be str (url/path) or bytes")


def coerce_send_opts(
        opts: Optional[Union[SendOpts, Dict[str, Any]]],
) -> SendOpts:
    if opts is None:
        return SendOpts()
    if isinstance(opts, SendOpts):
        _coerce_reply_target_gone(opts.reply_target_gone)
        return opts
    if not isinstance(opts, dict):
        raise TypeError("send opts must be SendOpts or dict")
    return SendOpts(
        reply_to=_dict_get_any(opts, ("replyTo", "reply_to")),
        reply_in_thread=_dict_get_any(opts, ("replyInThread", "reply_in_thread")),
        receive_id=_dict_get_any(opts, ("receiveId", "receive_id")),
        receive_id_type=_dict_get_any(opts, ("receiveIdType", "receive_id_type")),
        uuid=opts.get("uuid"),
        reply_target_gone=_coerce_reply_target_gone(
            _dict_get_any(opts, ("replyTargetGone", "reply_target_gone"))
        ),
    )


def _dict_get_any(d: Dict[str, Any], keys) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return None


def _coerce_reply_target_gone(value: Any) -> str:
    value = value or "fresh"
    if value not in ("fresh", "fail"):
        raise ValueError(f"invalid reply_target_gone: {value}")
    return value


def _coerce_caption(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise TypeError("caption must be a string")
    return value


def result_from_raw(raw: Any, *, message_id: Optional[str] = None) -> SendResult:
    if not isinstance(raw, dict):
        return SendResult.ok(message_id=message_id)
    code = raw.get("code", 0)
    if code == 0:
        return SendResult.ok(message_id=message_id, raw=raw)
    return SendResult.fail(
        SendError(
            code=FeishuChannelErrorCode.UNKNOWN,
            retryable=False,
            raw_code=int(code),
            hint=raw.get("msg"),
        ),
        raw=raw,
    )


async def maybe_await(v: Any) -> Any:
    if inspect.isawaitable(v):
        return await v
    return v


def obj_to_dict(obj: Any) -> Dict[str, Any]:
    """Marshal SDK event objects to plain dicts via the shared JSON encoder."""
    if isinstance(obj, dict):
        return obj
    try:
        s = JSON.marshal(obj)
        if not s:
            return {}
        parsed = json.loads(s)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:  # pragma: no cover
        return {}
