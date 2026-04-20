"""Per-type MessageContent → (content_text, resources) converters.

Each converter is a pure function ``convert(content) -> (str, List[ResourceDescriptor])``.
The ``REGISTRY`` maps concrete content types to their converter. The top-level
:func:`lark_oapi.channel.normalize.flatten.flatten` dispatches via this table
and falls back to :mod:`.fallback` for unknown variants.

Layout mirrors node-sdk's ``channel/normalize/converters/*.ts``.
"""

from typing import Any, Callable, Dict, List, Tuple

from ...types import (
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
    PostContent,
    ResourceDescriptor,
    ShareCalendarEventContent,
    ShareChatContent,
    ShareUserContent,
    StickerContent,
    SystemContent,
    TextContent,
    TodoContent,
    VideoChatContent,
    VoteContent,
)
from . import (
    audio,
    calendar,
    fallback,
    file,
    folder,
    hongbao,
    image,
    interactive,
    location,
    merge_forward,
    post,
    share,
    sticker,
    system,
    text,
    todo,
    video,
    video_chat,
    vote,
)

Converter = Callable[[Any], Tuple[str, List[ResourceDescriptor]]]

REGISTRY: Dict[type, Converter] = {
    TextContent: text.convert,
    PostContent: post.convert,
    ImageContent: image.convert,
    FileContent: file.convert,
    AudioContent: audio.convert,
    MediaContent: video.convert,
    StickerContent: sticker.convert,
    InteractiveContent: interactive.convert,
    ShareChatContent: share.convert_chat,
    ShareUserContent: share.convert_user,
    SystemContent: system.convert,
    LocationContent: location.convert,
    FolderContent: folder.convert,
    HongbaoContent: hongbao.convert,
    VideoChatContent: video_chat.convert,
    CalendarContent: calendar.convert,
    GeneralCalendarContent: calendar.convert_general,
    ShareCalendarEventContent: calendar.convert_share_event,
    VoteContent: vote.convert,
    TodoContent: todo.convert,
    MergeForwardContent: merge_forward.convert,
}

__all__ = ["REGISTRY", "Converter", "fallback"]
