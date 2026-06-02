"""Outbound sender: translates OutboundMessage → Lark SDK calls.

The sender is deliberately I/O-light: it composes the right request body and
delegates to a caller-supplied :class:`SendDriver`. In production the driver
is backed by ``lark_oapi.Client``; tests inject fakes.

Media-upload concerns (resolving a :class:`MediaSource` into a Lark
``file_key``) live in :mod:`.media.uploader`.
"""

import inspect
import json
import uuid
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

from lark_oapi.core.log import logger

from ..config import OutboundConfig
from ..errors import (
    FeishuChannelError,
    FeishuChannelErrorCode,
    SendError,
    classify_error,
    is_format_error,
    is_reply_target_gone,
)
from .retry import with_retry
from .media.uploader import resolve_media_key
from ..types import (
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
    SendResult,
)
from .markdown import markdown_to_post_ast, split_with_code_fences
from .routing import infer_receive_id_type

# ----------------------------------------------------------------------------
# Plain-text chunking — kept local to the sender (node-aligned). Only the
# markdown-aware `split_with_code_fences` lives in :mod:`.markdown.splitter`.
# ----------------------------------------------------------------------------

_ChunkMode = str  # "newline" | "paragraph" | "none"


def chunk_text(text: str, limit: int = 3500, mode: _ChunkMode = "newline") -> list:
    """Split ``text`` into ordered chunks of <= ``limit`` chars.

    - ``newline``: prefers breaking at the last ``\\n`` within the window.
    - ``paragraph``: prefers breaking at blank-line boundaries.
    - ``none``: hard slice at ``limit`` chars.
    """
    if not text:
        return []
    if limit <= 0:
        return [text]
    if len(text) <= limit:
        return [text]
    if mode == "none":
        return [text[i: i + limit] for i in range(0, len(text), limit)]
    if mode == "paragraph":
        return _chunk_by_delim(text, limit, delim="\n\n")
    return _chunk_by_delim(text, limit, delim="\n")


def _chunk_by_delim(text: str, limit: int, delim: str) -> list:
    chunks = []
    i = 0
    n = len(text)
    delim_len = len(delim)
    while i < n:
        if n - i <= limit:
            chunks.append(text[i:])
            break
        window = text[i: i + limit]
        idx = window.rfind(delim)
        if idx <= 0:
            chunks.append(window)
            i += limit
        else:
            chunks.append(window[:idx])
            i += idx + delim_len
    return [c for c in chunks if c]


# ----------------------------------------------------------------------------
# Driver protocol — the thin seam between the sender and the Lark HTTP client.
# Each method takes a dict "body" payload + keyword args and returns a dict
# with at least {code, msg, data?}. Async or sync callables are both allowed.
# ----------------------------------------------------------------------------

SendFn = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]


@dataclass
class SendDriver:
    create_message: SendFn
    reply_message: SendFn
    patch_message: Optional[SendFn] = None
    delete_message: Optional[SendFn] = None
    forward_message: Optional[SendFn] = None
    upload_image: Optional[SendFn] = None
    upload_file: Optional[SendFn] = None


class _OversizeHookFailure(Exception):
    """Internal: marker for an OutboundConfig.on_oversize hook exception so
    the broad ``except Exception`` in send() can re-raise the original
    instead of swallowing into SendResult.fail(UNKNOWN). Hook exceptions
    propagate to the caller without silent fallback.
    """

    def __init__(self, original: BaseException):
        self.original = original
        super().__init__(str(original))


class _UnsupportedMediaCaption(Exception):
    """Internal: media caption shape is not supported by Lark post messages."""

    def __init__(self, media_kind: str):
        self.media_kind = media_kind
        super().__init__(
            f"{media_kind} caption is not supported by Lark post messages; "
            "send the caption as a separate message if two-message semantics are acceptable"
        )


async def _maybe_await(v: Any) -> Any:
    if inspect.isawaitable(v):
        return await v
    return v


def _unwrap(result: Any) -> Dict[str, Any]:
    """Normalize driver output to a plain dict shape."""
    if result is None:
        return {"code": -1, "msg": "empty response"}
    if isinstance(result, dict):
        return result
    # If it's an object from the SDK with .code / .msg / .data, fall back.
    code = getattr(result, "code", None)
    if code is None:
        return {"code": -1, "msg": "unknown response"}
    data = getattr(result, "data", None)
    out = {"code": code, "msg": getattr(result, "msg", "") or ""}
    if data is not None:
        # data may be a model object; try to coerce to dict.
        if isinstance(data, dict):
            out["data"] = data
        else:
            try:
                out["data"] = {
                    k: getattr(data, k)
                    for k in dir(data)
                    if not k.startswith("_") and not callable(getattr(data, k))
                }
            except Exception:  # pragma: no cover - defensive
                out["data"] = {}
    return out


def _extract_message_id(resp: Dict[str, Any]) -> Optional[str]:
    data = resp.get("data") or {}
    if not isinstance(data, dict):
        return None
    return data.get("message_id") or data.get("id")


# ----------------------------------------------------------------------------
# Content builders — turn an OutboundMessage into a `msg_type` + content JSON.
# ----------------------------------------------------------------------------


def _build_text(msg: OutboundText) -> Dict[str, str]:
    # Inject <at> tags for mentioned identities so they get notified.
    at_prefix = ""
    for ident in msg.mentions or []:
        if ident and ident.open_id:
            name = ident.display_name or ""
            at_prefix += f'<at user_id="{ident.open_id}">{name}</at> '
    content = at_prefix + (msg.text or "")
    return {"msg_type": "text", "content": json.dumps({"text": content}, ensure_ascii=False)}


def _build_post(
        msg: OutboundPost,
        table_mode: str = "off",
        tag_md_mode: str = "structured",
) -> Dict[str, str]:
    """Build a Feishu post-message body.

    Feishu's ``im.v1.message.create`` expects ``content`` for ``msg_type=post``
    to be the JSON-serialised locale map directly (``{zh_cn: {title, content}}``)
    — NO outer ``{"post": ...}`` wrapper. Wrapping it yields server error
    ``230001 invalid message content``. Node SDK verified at sender.ts uses
    the same unwrapped shape.
    """
    if msg.post is not None:
        post = msg.post
    elif msg.markdown is not None:
        post = markdown_to_post_ast(
            msg.markdown,
            title=msg.title or "",
            mentions=list(msg.mentions or []),
            table_mode=table_mode,
            tag_md_mode=tag_md_mode,
        )
    else:
        post = {"zh_cn": {"title": msg.title or "", "content": [[{"tag": "text", "text": ""}]]}}
    return {"msg_type": "post", "content": json.dumps(post, ensure_ascii=False)}


def _build_media_caption_post(
        *,
        caption: str,
        media_node: Dict[str, Any],
        table_mode: str = "off",
        tag_md_mode: str = "structured",
) -> Dict[str, str]:
    post = markdown_to_post_ast(
        caption,
        title="",
        table_mode=table_mode,
        tag_md_mode=tag_md_mode,
    )
    zh = post.setdefault("zh_cn", {"title": "", "content": []})
    rows = zh.setdefault("content", [])
    rows.append([media_node])
    return {"msg_type": "post", "content": json.dumps(post, ensure_ascii=False)}


def _build_card(msg: OutboundCard) -> Dict[str, str]:
    if msg.card_id:
        content = {"type": "card", "data": {"card_id": msg.card_id}}
    else:
        content = msg.card
    return {"msg_type": "interactive", "content": json.dumps(content, ensure_ascii=False)}


def _build_image(image_key: str) -> Dict[str, str]:
    return {"msg_type": "image", "content": json.dumps({"image_key": image_key}, ensure_ascii=False)}


def _build_file(file_key: str) -> Dict[str, str]:
    return {"msg_type": "file", "content": json.dumps({"file_key": file_key}, ensure_ascii=False)}


def _build_audio(file_key: str) -> Dict[str, str]:
    return {"msg_type": "audio", "content": json.dumps({"file_key": file_key}, ensure_ascii=False)}


def _build_video(file_key: str) -> Dict[str, str]:
    return {"msg_type": "media", "content": json.dumps({"file_key": file_key}, ensure_ascii=False)}


def _build_share_chat(chat_id: str) -> Dict[str, str]:
    return {
        "msg_type": "share_chat",
        "content": json.dumps({"chat_id": chat_id}, ensure_ascii=False),
    }


def _build_share_user(user_id: str) -> Dict[str, str]:
    return {
        "msg_type": "share_user",
        "content": json.dumps({"user_id": user_id}, ensure_ascii=False),
    }


def _build_sticker(file_key: str) -> Dict[str, str]:
    return {
        "msg_type": "sticker",
        "content": json.dumps({"file_key": file_key}, ensure_ascii=False),
    }


# ----------------------------------------------------------------------------
# Sender
# ----------------------------------------------------------------------------


class OutboundSender:
    def __init__(
            self,
            driver: SendDriver,
            config: Optional[OutboundConfig] = None,
            *,
            on_success: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._driver = driver
        self._config = config or OutboundConfig()
        # Optional callback invoked with the fresh message_id after each
        # successful send — used by the channel to track own messages for the
        # reaction 'own' filter.
        self._on_success: Optional[Callable[[str], None]] = on_success
        # Retry / SSRF knobs are read from ``self._config.retry`` and
        # ``self._config.ssrf_allowlist`` at call time (see ``with_retry``
        # invocations below and ``resolve_media_key`` call sites).

    def _markdown_modes(self) -> Tuple[str, str]:
        conv = self._config.markdown_converter
        if getattr(conv, "enabled", True):
            return conv.table_mode, getattr(conv, "tag_md_mode", "structured")
        return "off", "structured"

    async def materialize_for_edit(self, msg: OutboundMessage) -> Dict[str, str]:
        """Materialize exactly one text/post body for message editing.

        Unlike send materialization, this method does not chunk, does not call
        the oversize hook, and does not apply reply or receive-id semantics.
        """
        if isinstance(msg, OutboundText):
            return _build_text(msg)
        if isinstance(msg, OutboundPost):
            table_mode, tag_md_mode = self._markdown_modes()
            return _build_post(msg, table_mode=table_mode, tag_md_mode=tag_md_mode)
        raise TypeError(
            f"materialize_for_edit: unsupported message type {type(msg).__name__}; "
            "only OutboundText and OutboundPost are editable"
        )

    async def send(
            self,
            message: OutboundMessage,
            *,
            receive_id: Optional[str] = None,
            receive_id_type: Optional[str] = None,
            reply_to: Optional[str] = None,
            reply_in_thread: Optional[bool] = None,
            reply_target_gone: str = "fresh",
            uuid_: Optional[str] = None,
    ) -> SendResult:
        """Route a single OutboundMessage through the driver.

        Caller supplies either `receive_id` or `reply_to`. If both are given,
        reply wins — we use `/im/v1/messages/:id/reply`.
        """
        try:
            body_list = await self._materialize(
                message,
                chat_id=receive_id or "",
                receive_id_type=receive_id_type or "",
            )
        except _OversizeHookFailure as f:
            # Hook exceptions propagate to the caller without fallback.
            raise f.original from f.original
        except _UnsupportedMediaCaption as e:
            logger.warning("outbound: unsupported media caption: %s", e)
            return SendResult.fail(SendError(
                code=FeishuChannelErrorCode.FORMAT_ERROR,
                retryable=False,
                hint=str(e),
            ))
        except FeishuChannelError as e:
            # Preserve the typed error code (SSRF_BLOCKED, UPLOAD_FAILED, …)
            # from the uploader / ssrf guard; wrapping into UNKNOWN loses
            # the signal callers want to match on.
            logger.warning("outbound: materialize blocked: %s", e)
            return SendResult.fail(SendError(
                code=e.code, retryable=False, hint=str(e),
            ))
        except Exception as e:
            logger.exception("outbound: materialize failed: %s", e)
            return SendResult.fail(SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=False, hint=str(e)))

        if not body_list:
            return SendResult.fail(SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=False, hint="empty body"))

        # Collect every successful chunk's message_id. For single-chunk
        # messages we return the familiar ``SendResult.ok(message_id=...)``.
        # For multi-chunk (long markdown / post → multiple POST /messages
        # requests), we also populate ``chunk_ids`` so callers can observe
        # that the logical message was split. Node-sdk aligned.
        chunk_message_ids: List[str] = []
        last_result: SendResult = SendResult.fail(SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=False))
        for idx, body in enumerate(body_list):
            req_uuid = uuid_ if (idx == 0 and uuid_) else str(uuid.uuid4())
            # Only apply `reply_to` to the first chunk; subsequent chunks are
            # fresh messages so they all render in the original chat.
            effective_reply_to = reply_to if idx == 0 else None
            result = await self._send_one_with_fallback(
                body=body,
                receive_id=receive_id,
                receive_id_type=receive_id_type,
                reply_to=effective_reply_to,
                reply_in_thread=reply_in_thread,
                reply_target_gone=reply_target_gone,
                uuid_=req_uuid,
            )
            last_result = result
            if not result.success:
                return result
            if result.message_id:
                chunk_message_ids.append(result.message_id)
        # Augment the final success result with chunk_ids when >1 chunk.
        if len(chunk_message_ids) > 1:
            return SendResult.ok(
                message_id=chunk_message_ids[0],
                raw=last_result.raw,
                chunk_ids=list(chunk_message_ids),
            )
        return last_result

    async def _send_one_with_fallback(
            self,
            *,
            body: Dict[str, str],
            receive_id: Optional[str],
            receive_id_type: Optional[str],
            reply_to: Optional[str],
            reply_in_thread: Optional[bool],
            reply_target_gone: str,
            uuid_: str,
    ) -> SendResult:
        """One send attempt with retry + two graceful downgrades.

        - `target_revoked` when replying → retry as a fresh create.
        - `format_error` on `post` → downgrade to plain text.
        """

        async def attempt(_: int) -> SendResult:
            if reply_to:
                return await self._reply(reply_to, body, reply_in_thread, uuid_)
            rid = receive_id or ""
            rit = receive_id_type or infer_receive_id_type(rid)
            return await self._create(rid, rit, body, uuid_)

        result = await with_retry(
            attempt,
            max_attempts=self._config.retry.max_attempts,
            base_delay_ms=self._config.retry.base_delay_ms,
        )
        if result.success or result.error is None:
            return result

        err = result.error
        # Downgrade 1: reply target gone → fresh send
        if is_reply_target_gone(err.code) and reply_to:
            if reply_target_gone == "fail":
                return result
            logger.info("outbound: reply target gone, retrying as fresh message")

            async def fresh(_: int) -> SendResult:
                rid = receive_id or ""
                rit = receive_id_type or infer_receive_id_type(rid)
                return await self._create(rid, rit, body, uuid_)

            return await with_retry(fresh, max_attempts=self._config.retry.max_attempts,
                                    base_delay_ms=self._config.retry.base_delay_ms)

        # Downgrade 2: post rejected → fallback to plain text
        if is_format_error(err.code) and body.get("msg_type") == "post":
            logger.info("outbound: post format rejected, falling back to plain text")
            plain = _post_to_plain_text_from_body(body.get("content", ""))
            if plain:
                text_body = {"msg_type": "text", "content": json.dumps({"text": plain}, ensure_ascii=False)}

                async def fallback(_: int) -> SendResult:
                    if reply_to:
                        return await self._reply(reply_to, text_body, reply_in_thread, uuid_)
                    rid = receive_id or ""
                    rit = receive_id_type or infer_receive_id_type(rid)
                    return await self._create(rid, rit, text_body, uuid_)

                return await with_retry(fallback, max_attempts=self._config.retry.max_attempts,
                                        base_delay_ms=self._config.retry.base_delay_ms)

        return result

    async def _materialize(
            self,
            msg: OutboundMessage,
            *,
            chat_id: str = "",
            receive_id_type: str = "",
    ) -> List[Dict[str, str]]:
        if isinstance(msg, OutboundText):
            text = msg.text or ""
            replacement = await self._maybe_oversize_hook(
                text, chat_id=chat_id, receive_id_type=receive_id_type,
            )
            if replacement:
                replaced = OutboundText(text=replacement, mentions=msg.mentions)
                return [_build_text(replaced)]

            # Chunking for long text
            chunks = chunk_text(
                text,
                limit=self._config.text_chunk_limit,
                mode=self._config.chunk_mode,
            ) or [""]
            out: List[Dict[str, str]] = []
            for i, chunk in enumerate(chunks):
                part = OutboundText(
                    text=chunk,
                    mentions=msg.mentions if i == 0 else [],
                )
                out.append(_build_text(part))
            return out
        if isinstance(msg, OutboundPost):
            table_mode, tag_md_mode = self._markdown_modes()
            # Markdown-sourced posts get split (code-fence aware) when the raw
            # markdown exceeds the configured chunk limit; each chunk becomes
            # its own post body. Pre-built ``msg.post`` ASTs are sent as-is —
            # they're opaque to us. Mentions go only on the first chunk so
            # ``@user`` doesn't fire again on every fragment.
            if msg.markdown is not None and len(msg.markdown) > self._config.text_chunk_limit:
                replacement = await self._maybe_oversize_hook(
                    msg.markdown, chat_id=chat_id, receive_id_type=receive_id_type,
                )
                if replacement:
                    replaced = OutboundText(text=replacement, mentions=msg.mentions)
                    return [_build_text(replaced)]
                md_chunks = split_with_code_fences(
                    msg.markdown, self._config.text_chunk_limit,
                )
                out: List[Dict[str, str]] = []
                for i, chunk in enumerate(md_chunks):
                    part = OutboundPost(
                        markdown=chunk,
                        title=msg.title if i == 0 else "",
                        mentions=msg.mentions if i == 0 else [],
                    )
                    out.append(_build_post(part, table_mode=table_mode, tag_md_mode=tag_md_mode))
                return out
            return [_build_post(msg, table_mode=table_mode, tag_md_mode=tag_md_mode)]
        if isinstance(msg, OutboundCard):
            return [_build_card(msg)]
        allowlist = self._config.ssrf_allowlist
        if isinstance(msg, OutboundImage):
            key = await resolve_media_key(
                self._driver, msg.source, "image", ssrf_allowlist=allowlist
            )
            if not key:
                return []
            if msg.caption:
                table_mode, tag_md_mode = self._markdown_modes()
                return [_build_media_caption_post(
                    caption=msg.caption,
                    media_node={"tag": "img", "image_key": key},
                    table_mode=table_mode,
                    tag_md_mode=tag_md_mode,
                )]
            return [_build_image(key)]
        if isinstance(msg, OutboundFile):
            if msg.caption:
                raise _UnsupportedMediaCaption("file")
            key = await resolve_media_key(
                self._driver, msg.source, "file",
                file_name=msg.file_name, ssrf_allowlist=allowlist,
            )
            if not key:
                return []
            return [_build_file(key)]
        if isinstance(msg, OutboundAudio):
            if msg.caption:
                raise _UnsupportedMediaCaption("audio")
            key = await resolve_media_key(
                self._driver, msg.source, "file",
                file_type="opus", ssrf_allowlist=allowlist,
            )
            return [_build_audio(key)] if key else []
        if isinstance(msg, OutboundVideo):
            key = await resolve_media_key(
                self._driver, msg.source, "file",
                file_type="mp4", ssrf_allowlist=allowlist,
            )
            if msg.caption and key:
                table_mode, tag_md_mode = self._markdown_modes()
                return [_build_media_caption_post(
                    caption=msg.caption,
                    media_node={"tag": "media", "file_key": key},
                    table_mode=table_mode,
                    tag_md_mode=tag_md_mode,
                )]
            return [_build_video(key)] if key else []
        if isinstance(msg, OutboundShareChat):
            return [_build_share_chat(msg.chat_id)] if msg.chat_id else []
        if isinstance(msg, OutboundShareUser):
            return [_build_share_user(msg.user_id)] if msg.user_id else []
        if isinstance(msg, OutboundSticker):
            return [_build_sticker(msg.file_key)] if msg.file_key else []
        return []

    async def _maybe_oversize_hook(
            self, text: str, *, chat_id: str, receive_id_type: str,
    ) -> Optional[str]:
        """Return non-empty replacement when the hook supplies one.

        - No hook configured -> None (caller chunks normally).
        - text within limit -> None (no oversize).
        - hook returns None / empty -> None (fallback).
        - hook returns non-empty str -> that string (single send).
        - hook raises -> wrapped in _OversizeHookFailure so the caller's
          broad `except Exception` doesn't accidentally swallow it; send()
          unwraps and re-raises the original.
        """
        hook = self._config.on_oversize
        if hook is None:
            return None
        if len(text) <= self._config.text_chunk_limit:
            return None
        from ..config import OversizeContext
        estimated = max(
            1,
            (len(text) + self._config.text_chunk_limit - 1) // self._config.text_chunk_limit,
        )
        ctx = OversizeContext(
            text=text,
            chat_id=chat_id,
            receive_id_type=receive_id_type,
            estimated_chunks=estimated,
        )
        try:
            result = await hook(ctx)
        except Exception as e:
            raise _OversizeHookFailure(e) from e
        if result:
            return result
        return None

    async def _create(
            self,
            receive_id: str,
            receive_id_type: str,
            body: Dict[str, str],
            uuid_: str,
    ) -> SendResult:
        try:
            raw = await _maybe_await(
                self._driver.create_message(
                    receive_id_type=receive_id_type,
                    receive_id=receive_id,
                    msg_type=body["msg_type"],
                    content=body["content"],
                    uuid=uuid_,
                )
            )
        except Exception as e:
            logger.exception("outbound: create_message raised: %s", e)
            return SendResult.fail(SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=True, hint=str(e)))
        result = self._to_result(raw)
        if not result.success:
            content_len = len(body.get("content", "") or "")
            logger.warning(
                "outbound: create_message FAILED receive_id_type=%s receive_id=%s msg_type=%s "
                "request_content_len=%s response=%s",
                receive_id_type, receive_id, body.get("msg_type"),
                content_len,
                result.raw,
            )
        return result

    async def _reply(
            self,
            message_id: str,
            body: Dict[str, str],
            reply_in_thread: Optional[bool],
            uuid_: str,
    ) -> SendResult:
        try:
            kwargs: Dict[str, Any] = {
                "message_id": message_id,
                "msg_type": body["msg_type"],
                "content": body["content"],
                "uuid": uuid_,
            }
            if reply_in_thread is not None:
                kwargs["reply_in_thread"] = reply_in_thread
            raw = await _maybe_await(self._driver.reply_message(**kwargs))
        except Exception as e:
            logger.exception("outbound: reply_message raised: %s", e)
            return SendResult.fail(SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=True, hint=str(e)))
        result = self._to_result(raw)
        if not result.success:
            content_len = len(body.get("content", "") or "")
            logger.warning(
                "outbound: reply_message FAILED message_id=%s msg_type=%s "
                "request_content_len=%s response=%s",
                message_id, body.get("msg_type"),
                content_len,
                result.raw,
            )
        return result

    def _to_result(self, raw: Any) -> SendResult:
        resp = _unwrap(raw)
        code = resp.get("code") or 0
        if code == 0:
            mid = _extract_message_id(resp)
            if mid and self._on_success is not None:
                try:
                    self._on_success(mid)
                except Exception as e:  # pragma: no cover - defensive
                    logger.debug("outbound: _on_success hook raised: %s", e)
            return SendResult.ok(message_id=mid, raw=resp)
        return SendResult.fail(
            classify_error(int(code), resp.get("msg") or ""),
            raw=resp,
        )


def _post_to_plain_text_from_body(content: str) -> str:
    """Extract a best-effort plain-text rendering from a post JSON body.

    ``content`` is the already-serialised post body emitted by
    :func:`_build_post`, i.e. ``{zh_cn: {title, content: [[...]]}}`` — NOT
    wrapped in an outer ``{"post": ...}``. Used by the format_error → plain-
    text downgrade path. Returns empty string on any structural mismatch.
    """
    try:
        data = json.loads(content)
        if not isinstance(data, dict) or not data:
            return ""
        locale = next(iter(data.values()))
        if not isinstance(locale, dict):
            return ""
        out_lines: List[str] = []
        title = locale.get("title")
        if title:
            out_lines.append(str(title))
        for para in locale.get("content") or []:
            pieces: List[str] = []
            for el in para or []:
                if not isinstance(el, dict):
                    continue
                if el.get("tag") == "text":
                    pieces.append(el.get("text") or "")
                elif el.get("tag") == "a":
                    pieces.append(el.get("text") or el.get("href") or "")
                elif el.get("tag") == "at":
                    pieces.append(f"@{el.get('user_name') or el.get('user_id') or ''}")
                elif el.get("tag") == "img":
                    pieces.append("[image]")
                elif el.get("tag") == "code_block":
                    pieces.append(el.get("text") or "")
            out_lines.append("".join(pieces))
        return "\n".join(l for l in out_lines if l is not None).strip() or "[message]"
    except Exception:
        return ""
