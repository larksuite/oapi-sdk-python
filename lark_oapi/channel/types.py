"""Unified data types exposed to channel handlers.

Design goal: a single `MessageContent` discriminated union covers all 19 Lark
message types so that handlers can `if content.kind == 'text': ...` without
having to know the original wire format.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

from .errors import SendError

# ----------------------------------------------------------------------------
# Conversation / Identity
# ----------------------------------------------------------------------------

ChatType = Literal["p2p", "group", "topic", "unknown"]


@dataclass
class Conversation:
    chat_id: str
    chat_type: ChatType = "unknown"
    thread_id: Optional[str] = None


@dataclass
class Identity:
    open_id: str
    union_id: Optional[str] = None
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    is_bot: bool = False


@dataclass
class Mention:
    """A resolved @-mention occurrence in inbound message text.

    Each mention pairs the placeholder ``key`` (e.g. ``@_user_1``) with the
    identity it resolves to.
    """

    key: str  # the placeholder key, e.g. @_user_1
    open_id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None
    is_bot: bool = False
    union_id: Optional[str] = None
    tenant_key: Optional[str] = None


# ----------------------------------------------------------------------------
# Media reference
# ----------------------------------------------------------------------------


@dataclass
class MediaRef:
    """Points to a media object already stored inside Lark (file_key or image_key)."""

    key: str
    media_type: Literal["image", "file", "audio", "video"]
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    duration_ms: Optional[int] = None


ResourceType = Literal["image", "file", "audio", "video", "sticker"]


@dataclass
class ResourceDescriptor:
    """Media descriptor exposed alongside the flattened ``content_text``.

    Each descriptor carries everything needed to download the resource via
    ``channel.download_resource(file_key, type)``, independent of which
    ``MessageContent`` variant originally carried it.
    """

    type: ResourceType
    file_key: str
    file_name: Optional[str] = None
    duration_ms: Optional[int] = None
    cover_image_key: Optional[str] = None


# ----------------------------------------------------------------------------
# MessageContent union — 19 kinds + unknown
# ----------------------------------------------------------------------------
#
# Content dataclasses are **pipeline-populated**, not directly user-constructed.
# The inbound :class:`InboundPipeline` reads a Feishu message payload, selects
# the right ``*Content`` class based on the wire ``message_type``, and fills
# in the fields. Test fixtures may instantiate them directly; application
# code generally shouldn't.
#
# The ``kind`` field on each class is a :class:`typing.Literal` discriminator
# that matches Feishu's wire-protocol ``message_type`` string. It has a
# default because Python 3.8 ``@dataclass`` doesn't support ``kw_only``
# required fields after defaulted ones (``raw`` on the base); treat ``kind``
# as non-user-settable.
# ----------------------------------------------------------------------------


@dataclass
class _BaseContent:
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TextContent(_BaseContent):
    kind: Literal["text"] = "text"
    text: str = ""


@dataclass
class PostContent(_BaseContent):
    kind: Literal["post"] = "post"
    title: str = ""
    text: str = ""  # plain-text rendering (best-effort)
    post: Dict[str, Any] = field(default_factory=dict)  # raw post AST by locale


@dataclass
class ImageContent(_BaseContent):
    kind: Literal["image"] = "image"
    image_key: str = ""


@dataclass
class FileContent(_BaseContent):
    kind: Literal["file"] = "file"
    file_key: str = ""
    file_name: Optional[str] = None


@dataclass
class AudioContent(_BaseContent):
    kind: Literal["audio"] = "audio"
    file_key: str = ""
    duration_ms: Optional[int] = None


@dataclass
class MediaContent(_BaseContent):
    kind: Literal["media"] = "media"
    file_key: str = ""
    image_key: Optional[str] = None  # cover
    duration_ms: Optional[int] = None
    file_name: Optional[str] = None


@dataclass
class StickerContent(_BaseContent):
    kind: Literal["sticker"] = "sticker"
    file_key: str = ""


@dataclass
class InteractiveContent(_BaseContent):
    kind: Literal["interactive"] = "interactive"
    card: Dict[str, Any] = field(default_factory=dict)  # unified v1/v2 JSON
    card_version: Literal["v1", "v2", "unknown"] = "unknown"


@dataclass
class ShareChatContent(_BaseContent):
    kind: Literal["share_chat"] = "share_chat"
    chat_id: str = ""


@dataclass
class ShareUserContent(_BaseContent):
    kind: Literal["share_user"] = "share_user"
    user_id: str = ""


@dataclass
class SystemContent(_BaseContent):
    kind: Literal["system"] = "system"
    template: str = ""
    from_user: List[Dict[str, Any]] = field(default_factory=list)
    to_chatters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LocationContent(_BaseContent):
    kind: Literal["location"] = "location"
    name: str = ""
    longitude: Optional[float] = None
    latitude: Optional[float] = None


@dataclass
class FolderContent(_BaseContent):
    """Message carrying a shared Drive folder reference.

    ``file_key`` is the primary identifier on the wire (matches node's
    ``FolderContent.file_key``); without it the converter falls back to a
    ``[folder]`` placeholder.
    """

    kind: Literal["folder"] = "folder"
    file_key: str = ""
    file_name: str = ""
    file_size: Optional[int] = None


@dataclass
class RedPacketContent(_BaseContent):
    """Red-packet message.

    ``RedPacketContent`` is the preferred Python name; ``HongbaoContent`` is
    kept as a back-compat alias because the Feishu wire-protocol uses the
    Pinyin form ``hongbao`` in its message-type discriminator.
    """

    kind: Literal["hongbao"] = "hongbao"
    text: str = ""
    amount: Optional[int] = None


# Back-compat alias for the (ugly) name that mirrors Feishu's on-wire
# ``hongbao`` message-type discriminator. New code should prefer
# ``RedPacketContent``.
HongbaoContent = RedPacketContent


@dataclass
class GeneralCalendarContent(_BaseContent):
    """Generic calendar event share."""

    kind: Literal["general_calendar"] = "general_calendar"
    summary: str = ""
    start_time: Optional[int] = None
    end_time: Optional[int] = None


@dataclass
class ShareCalendarEventContent(_BaseContent):
    """A specific calendar event share (richer than `calendar`)."""

    kind: Literal["share_calendar_event"] = "share_calendar_event"
    summary: str = ""
    organizer: str = ""
    start_time: Optional[int] = None
    end_time: Optional[int] = None


@dataclass
class VideoChatContent(_BaseContent):
    kind: Literal["video_chat"] = "video_chat"
    topic: str = ""
    start_time: Optional[int] = None


@dataclass
class CalendarContent(_BaseContent):
    kind: Literal["calendar"] = "calendar"
    summary: str = ""
    start_time: Optional[int] = None
    end_time: Optional[int] = None


@dataclass
class VoteContent(_BaseContent):
    kind: Literal["vote"] = "vote"
    topic: str = ""
    options: List[str] = field(default_factory=list)


@dataclass
class TodoContent(_BaseContent):
    """Todo message.

    On the wire the ``summary`` field is a nested ``{title, content}`` object
    where ``content`` is a post-AST (paragraphs of text/link elements). The
    parser extracts plain ``title`` + ``body`` eagerly so the converter can
    format a rich ``<todo>`` block without re-walking the AST.
    """

    kind: Literal["todo"] = "todo"
    title: str = ""
    body: str = ""
    due_time: Optional[int] = None


@dataclass
class MergeForwardItem:
    """A single child message inside a merge_forward payload."""

    message_id: str
    sender_open_id: Optional[str] = None
    sender_name: Optional[str] = None
    create_time: Optional[int] = None
    content: Optional["MessageContent"] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MergeForwardContent(_BaseContent):
    kind: Literal["merge_forward"] = "merge_forward"
    loading: bool = False
    items: List[MergeForwardItem] = field(default_factory=list)
    truncated: bool = False
    error: Optional[str] = None


@dataclass
class UnknownContent(_BaseContent):
    kind: Literal["unknown"] = "unknown"
    message_type: str = ""


MessageContent = Union[
    TextContent,
    PostContent,
    ImageContent,
    FileContent,
    AudioContent,
    MediaContent,
    StickerContent,
    InteractiveContent,
    ShareChatContent,
    ShareUserContent,
    SystemContent,
    LocationContent,
    FolderContent,
    HongbaoContent,
    GeneralCalendarContent,
    ShareCalendarEventContent,
    VideoChatContent,
    CalendarContent,
    VoteContent,
    TodoContent,
    MergeForwardContent,
    UnknownContent,
]


# ----------------------------------------------------------------------------
# Reply
# ----------------------------------------------------------------------------


@dataclass
class ReplyRef:
    message_id: str
    text: Optional[str] = None
    sender_id: Optional[str] = None


# ----------------------------------------------------------------------------
# InboundMessage
# ----------------------------------------------------------------------------


@dataclass
class InboundMessage:
    """Inbound-normalized message.

    Main views of the content:
    - `content`: discriminated-union (`TextContent` / `ImageContent` / ...)
      — Pythonic, type-checkable.
    - `content_text`: flat string rendering (Markdown for text/post, XML-like
      placeholders for media, merge_forward trees) — convenient for text-only
      pipelines.
    - `resources`: parallel list of media descriptors for download/routing.
    - `mentioned_bot`: convenience flag set by normalization/batching callers
      when any mention resolves to the current bot's open_id.
    """

    id: str
    create_time: int
    conversation: Conversation
    sender: Identity
    mentions: List[Mention] = field(default_factory=list)
    mentioned_all: bool = False
    reply: Optional[ReplyRef] = None
    content: MessageContent = field(default_factory=UnknownContent)
    raw: Dict[str, Any] = field(default_factory=dict)
    # Flat-text / resource views of `content`, populated by the pipeline
    content_text: str = ""
    resources: List[ResourceDescriptor] = field(default_factory=list)
    mentioned_bot: bool = False
    raw_content_type: str = ""
    batched_sources: Optional[List["InboundMessage"]] = None

    @property
    def message_id(self) -> str:
        """Alias for ``id`` — the message's stable identifier."""
        return self.id

    @property
    def chat_id(self) -> str:
        return self.conversation.chat_id

    @property
    def chat_type(self) -> str:
        return self.conversation.chat_type

    @property
    def sender_id(self) -> str:
        return self.sender.open_id

    @property
    def sender_name(self) -> Optional[str]:
        return self.sender.display_name

    @property
    def reply_to_message_id(self) -> Optional[str]:
        return self.reply.message_id if self.reply else None


# ----------------------------------------------------------------------------
# Outbound messages
# ----------------------------------------------------------------------------


@dataclass
class _OutBase:
    pass


@dataclass
class OutboundText(_OutBase):
    kind: Literal["text"] = "text"
    text: str = ""
    mentions: List[Identity] = field(default_factory=list)


@dataclass
class OutboundPost(_OutBase):
    kind: Literal["post"] = "post"
    markdown: Optional[str] = None
    post: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    mentions: List[Identity] = field(default_factory=list)


@dataclass
class OutboundCard(_OutBase):
    kind: Literal["card"] = "card"
    card: Dict[str, Any] = field(default_factory=dict)
    card_id: Optional[str] = None


MediaSourceKind = Literal["url", "file", "buffer", "key"]


@dataclass
class MediaSource:
    kind: MediaSourceKind
    url: Optional[str] = None
    path: Optional[str] = None
    buffer: Optional[bytes] = None
    key: Optional[str] = None


@dataclass
class OutboundImage(_OutBase):
    kind: Literal["image"] = "image"
    source: Optional[MediaSource] = None
    caption: Optional[str] = None


@dataclass
class OutboundFile(_OutBase):
    kind: Literal["file"] = "file"
    source: Optional[MediaSource] = None
    file_name: Optional[str] = None
    caption: Optional[str] = None


@dataclass
class OutboundAudio(_OutBase):
    kind: Literal["audio"] = "audio"
    source: Optional[MediaSource] = None
    caption: Optional[str] = None


@dataclass
class OutboundVideo(_OutBase):
    kind: Literal["video"] = "video"
    source: Optional[MediaSource] = None
    caption: Optional[str] = None


@dataclass
class OutboundShareChat(_OutBase):
    """Send a group chat "business card" referencing ``chat_id``.

    Feishu wire form: ``msg_type="share_chat"`` / ``content={"chat_id": "..."}``.
    """

    kind: Literal["share_chat"] = "share_chat"
    chat_id: str = ""


@dataclass
class OutboundShareUser(_OutBase):
    """Send a personal card referencing a user's ``open_id`` (or union_id).

    Feishu wire form: ``msg_type="share_user"`` / ``content={"user_id": "..."}``.
    """

    kind: Literal["share_user"] = "share_user"
    user_id: str = ""


@dataclass
class OutboundSticker(_OutBase):
    """Send a sticker by its ``file_key``.

    Feishu wire form: ``msg_type="sticker"`` / ``content={"file_key": "..."}``.
    """

    kind: Literal["sticker"] = "sticker"
    file_key: str = ""


OutboundMessage = Union[
    OutboundText,
    OutboundPost,
    OutboundCard,
    OutboundImage,
    OutboundFile,
    OutboundAudio,
    OutboundVideo,
    OutboundShareChat,
    OutboundShareUser,
    OutboundSticker,
]


# ----------------------------------------------------------------------------
# Send result
# ----------------------------------------------------------------------------


@dataclass
class SendResult:
    """The outcome of a single :meth:`FeishuChannel.send` or ``stream`` call.

    For messages that fit in one wire payload, only ``message_id`` is set.
    For messages that get split across multiple wire payloads (long
    markdown, long post — see :mod:`.outbound.sender._materialize`),
    ``chunk_ids`` lists **every** chunk's message_id in order, and
    ``message_id`` holds the first chunk for convenience / back-compat.
    ``chunk_ids`` is ``None`` when there was only one chunk. Aligned with
    node-sdk's ``SendResult.chunkIds?``.
    """

    success: bool
    message_id: Optional[str] = None
    error: Optional[SendError] = None
    raw: Optional[Dict[str, Any]] = None
    chunk_ids: Optional[List[str]] = None

    @classmethod
    def ok(
            cls,
            message_id: Optional[str] = None,
            raw: Optional[Dict[str, Any]] = None,
            chunk_ids: Optional[List[str]] = None,
    ) -> "SendResult":
        return cls(
            success=True, message_id=message_id, raw=raw, chunk_ids=chunk_ids,
        )

    @classmethod
    def fail(cls, error: SendError, raw: Optional[Dict[str, Any]] = None) -> "SendResult":
        return cls(success=False, error=error, raw=raw)


# ----------------------------------------------------------------------------
# Card payload
# ----------------------------------------------------------------------------


@dataclass
class CardPayload:
    """A finalised CardKit JSON object ready for the Lark API."""

    data: Dict[str, Any]
    version: Literal["v1", "v2"] = "v2"


# ----------------------------------------------------------------------------
# User Access Token
# ----------------------------------------------------------------------------


@dataclass
class UserAccessToken:
    """A resolved user access token (UAT) for a specific end-user.

    Holds both the short-lived access token and the refresh token (when
    granted), along with the scopes, user identity, and raw vendor response
    for diagnostics.
    """

    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None  # unix seconds
    refresh_expires_at: Optional[float] = None
    scopes: List[str] = field(default_factory=list)
    open_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


# Back-compat alias — existing code and tests import ``UAT`` directly. Kept
# for one release to ease migration; prefer ``UserAccessToken`` in new code.
UAT = UserAccessToken

# ----------------------------------------------------------------------------
# Send options / routing
# ----------------------------------------------------------------------------

ReceiveIdType = Literal["open_id", "chat_id", "user_id", "union_id", "email"]
ReplyTargetGoneBehavior = Literal["fresh", "fail"]


@dataclass
class SendOpts:
    reply_to: Optional[str] = None  # message_id — forces reply mode
    reply_in_thread: Optional[bool] = None
    receive_id: Optional[str] = None  # explicit target; overrides auto-routing
    receive_id_type: Optional[ReceiveIdType] = None
    uuid: Optional[str] = None
    reply_target_gone: ReplyTargetGoneBehavior = "fresh"


@dataclass
class Target:
    """Receiver spec for out-of-band sends (not tied to an inbound ctx)."""

    id: str
    id_type: ReceiveIdType = "chat_id"


# ---------------------------------------------------------------------------
# Event payload dataclasses passed to `channel.on(...)` handlers when using
# the FeishuChannel facade.
# ---------------------------------------------------------------------------


@dataclass
class EventOperator:
    """Who performed an action: ``open_id`` plus optional ``user_id`` / ``name``."""

    open_id: str = ""
    user_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class CardActionPayload:
    """Inner ``action`` field of a ``CardActionEvent``.

    ``value`` is the form/button data; ``tag`` identifies which element fired;
    ``name`` / ``option`` carry element-specific metadata.
    """

    value: Any = None
    tag: str = ""
    name: Optional[str] = None
    option: Optional[str] = None


@dataclass
class CardActionEvent:
    """Emitted to ``channel.on("cardAction", ...)`` handlers.

    Carries the ``message_id`` and ``chat_id`` of the source card plus the
    resolved ``operator`` and ``action`` payload.
    """

    message_id: str
    chat_id: str
    operator: EventOperator
    action: CardActionPayload
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReactionEvent:
    """Emitted to `channel.on("reaction", ...)` handlers."""

    message_id: str
    operator: EventOperator
    emoji_type: str
    action: str  # 'added' | 'removed'
    chat_id: Optional[str] = None
    chat_type: Optional[ChatType] = None
    action_time: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BotAddedEvent:
    """Emitted to `channel.on("botAdded", ...)` when the bot joins a chat."""

    chat_id: str
    operator: EventOperator
    chat_name: Optional[str] = None
    external: Optional[bool] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BotLeaveEvent:
    """Emitted to ``channel.on("botLeave", ...)`` when the bot is removed from a chat."""

    chat_id: str
    operator: EventOperator
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageReadEvent:
    """Emitted to `channel.on("messageRead", ...)` for read-receipt events."""

    reader: EventOperator
    message_ids: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatInfo:
    """Returned by ``channel.get_chat_info(chat_id)``."""

    chat_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    chat_type: ChatType = "unknown"
    owner_id: Optional[str] = None
    member_count: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)
