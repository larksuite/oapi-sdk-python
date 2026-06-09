"""Top-level inbound pipeline.

Orchestrates the flow:
    raw event → dedup → parse → async enrich (merge_forward, interactive,
    mentions, identity) → InboundMessage.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from lark_oapi.core.log import logger

from ..config import InboundConfig
from ..types import (
    Conversation,
    Identity,
    InboundMessage,
    InteractiveContent,
    Mention,
    MergeForwardContent,
    PostContent,
    ReplyRef,
    TextContent,
)
from .dedup import Deduper
from .flatten import flatten
from .interactive import fetch_interactive
from .mentions import (
    extract_mentions,
    parse_at_tags,
    resolve_mentions,
    text_has_mention_all,
)
from .merge_forward import MergeForwardExpander
from .registry import parse_message_content


@dataclass
class PipelineDeps:
    """External hooks the pipeline needs (all optional for testing)."""

    fetch_message: Optional[Callable[[str], Any]] = None
    resolve_names: Optional[Callable[[List[str]], Any]] = None
    resolve_identity: Optional[Callable[[str], Any]] = None


@dataclass
class PipelineConfig:
    inbound: InboundConfig = field(default_factory=InboundConfig)
    account_id: str = ""


def _to_chat_type(value: Optional[str]) -> str:
    if value in ("p2p", "group", "topic"):
        return value
    # Feishu sometimes uses "public"/"private" for chat_type.
    if value == "private":
        return "p2p"
    if value == "public":
        return "group"
    return "unknown"


def _sender_to_identity(sender: Any) -> Identity:
    """Normalize an event.sender payload (dict or EventSender) to Identity."""
    if isinstance(sender, dict):
        sid = sender.get("sender_id") or {}
        return Identity(
            open_id=sid.get("open_id") or "",
            union_id=sid.get("union_id"),
            user_id=sid.get("user_id"),
            is_bot=_is_bot_sender_type(sender.get("sender_type")),
        )
    sid = getattr(sender, "sender_id", None)
    return Identity(
        open_id=getattr(sid, "open_id", "") or "",
        union_id=getattr(sid, "union_id", None),
        user_id=getattr(sid, "user_id", None),
        is_bot=_is_bot_sender_type(getattr(sender, "sender_type", None)),
    )


def _is_bot_sender_type(sender_type: Any) -> bool:
    return sender_type in {"bot", "app"}


def _message_to_dict(msg: Any) -> Dict[str, Any]:
    if isinstance(msg, dict):
        return msg
    out: Dict[str, Any] = {}
    for field_name in (
            "message_id",
            "root_id",
            "parent_id",
            "create_time",
            "update_time",
            "chat_id",
            "thread_id",
            "chat_type",
            "message_type",
            "content",
            "mentions",
            "user_agent",
    ):
        out[field_name] = getattr(msg, field_name, None)
    return out


class InboundPipeline:
    def __init__(
            self,
            cfg: PipelineConfig,
            deps: PipelineDeps,
            deduper: Optional[Deduper] = None,
    ) -> None:
        self._cfg = cfg
        self._deps = deps
        self._deduper = deduper
        self._expander = MergeForwardExpander(
            fetch_message=deps.fetch_message,
            resolve_names=deps.resolve_names,
            max_depth=cfg.inbound.merge_forward_max_depth,
            max_items=cfg.inbound.merge_forward_max_items,
        )

    async def process(
            self,
            event_id: Optional[str],
            message_event: Any,
            sender: Any,
    ) -> Optional[InboundMessage]:
        """Return InboundMessage or None if the event was deduped / filtered."""
        msg = _message_to_dict(message_event)
        message_id: str = msg.get("message_id") or ""

        if self._deduper is not None:
            ok = self._deduper.check_and_mark(
                self._cfg.account_id or "", event_id, message_id
            )
            if not ok:
                logger.debug("inbound: dedup hit for %s / %s", event_id, message_id)
                return None

        message_type = msg.get("message_type") or ""
        # Media capability gate (drop the message if that type is disabled)
        media_caps = self._cfg.inbound.media_capabilities
        gate_map = {
            "image": media_caps.image,
            "audio": media_caps.audio,
            "media": media_caps.video,
            "video": media_caps.video,
            "file": media_caps.file,
            "sticker": media_caps.sticker,
        }
        if message_type in gate_map and not gate_map[message_type]:
            logger.debug("inbound: message_type %s disabled by media_caps", message_type)
            return None

        content = parse_message_content(message_type, msg.get("content"))

        # Process mentions for text / post (node-aligned: extract → resolve).
        raw_mentions = msg.get("mentions") or []
        ext = extract_mentions(raw_mentions)
        mentions: List[Mention] = list(ext.mention_list)
        mentioned_all = ext.mentioned_all
        if isinstance(content, TextContent):
            # Feishu frequently ships ``@all`` messages with
            # ``mentions = null`` — the only signal is an ``@_all``
            # placeholder in ``content.text``. Without this probe the
            # policy gate never sees ``mentioned_all=True`` so
            # ``respond_to_mention_all`` / ``mention_all_blocked`` go
            # silently skipped.
            if not mentioned_all and text_has_mention_all(content.text):
                mentioned_all = True
            content.text = resolve_mentions(content.text, ext)
        elif isinstance(content, PostContent):
            if not mentioned_all and text_has_mention_all(content.text):
                mentioned_all = True
            content.text = resolve_mentions(content.text, ext)
            at_mentions, at_all, stripped = parse_at_tags(content.text)
            content.text = stripped
            # Merge <at>-tag mentions in (dedup by open_id/user_id/key).
            seen = {m.open_id or m.user_id or m.key for m in mentions}
            for m in at_mentions:
                sig = m.open_id or m.user_id or m.key
                if sig in seen:
                    continue
                seen.add(sig)
                mentions.append(m)
            mentioned_all = mentioned_all or at_all

        # Async enrichment: merge_forward expansion
        if (
                isinstance(content, MergeForwardContent)
                and self._cfg.inbound.expand_merge_forward
                and self._deps.fetch_message is not None
                and message_id
        ):
            content = await self._expander.expand(message_id)

        # Async enrichment: interactive card re-fetch
        if (
                isinstance(content, InteractiveContent)
                and self._cfg.inbound.fetch_interactive_card
                and self._deps.fetch_message is not None
                and message_id
        ):
            fetched = await fetch_interactive(message_id, self._deps.fetch_message)
            if fetched is not None:
                # keep raw from the original event
                fetched.raw = content.raw or fetched.raw
                content = fetched

        # Build conversation + reply ref
        conversation = Conversation(
            chat_id=msg.get("chat_id") or "",
            chat_type=_to_chat_type(msg.get("chat_type")),
            thread_id=msg.get("thread_id") or None,
        )

        reply: Optional[ReplyRef] = None
        parent_id = msg.get("parent_id") or ""
        root_id = msg.get("root_id") or ""
        if parent_id and parent_id != root_id:
            reply = ReplyRef(message_id=parent_id)

        sender_identity = _sender_to_identity(sender)
        # Fill sender display name from name cache / resolver if available.
        if not sender_identity.display_name and self._deps.resolve_names and sender_identity.open_id:
            try:
                import inspect

                result = self._deps.resolve_names([sender_identity.open_id])
                if inspect.isawaitable(result):
                    result = await result
                if isinstance(result, dict):
                    sender_identity.display_name = result.get(sender_identity.open_id) or sender_identity.display_name
            except Exception as e:  # pragma: no cover - defensive
                logger.debug("inbound: resolve sender name failed: %s", e)

        # Flat-string + resource-descriptor views of `content`. Re-flatten
        # every time in case merge_forward expansion or interactive re-fetch
        # changed the content kind since the initial parse.
        flat_text, resources = flatten(content)

        # Node-aligned second pass: resolve any ``@_user_N`` placeholder still
        # in the rendered text. This catches placeholders embedded in nested
        # merge_forward child content (parsed but not yet resolved because
        # flatten walks children sync without a ctx). Idempotent on text that
        # contains no placeholders.
        flat_text = resolve_mentions(flat_text, ext)

        return InboundMessage(
            id=message_id,
            create_time=_int_or_zero(msg.get("create_time")),
            conversation=conversation,
            sender=sender_identity,
            mentions=mentions,
            mentioned_all=mentioned_all,
            reply=reply,
            content=content,
            raw=msg if isinstance(msg, dict) else {},
            content_text=flat_text,
            resources=resources,
            raw_content_type=message_type,
        )


def _int_or_zero(v: Any) -> int:
    try:
        return int(v) if v is not None else 0
    except (TypeError, ValueError):
        return 0
