"""Media batching: debounce + bundle consecutive compatible media messages.

Parallel to ``ChatPipelineManager`` but with simpler semantics:

- Key: ``(chat_id, kind, reply_to, thread_id)``.
- Compatible run: same key, same kind, within ``delay_ms``.
- Incompatible push (different kind, or text intervenes) flushes the
  current batch first, then starts a new one with the new message.
- ``max_items`` cap: flushes the current batch and starts fresh.

Output is a single ``InboundMessage`` whose ``batched_sources`` carries the
ordered list of source messages. The merged message is the last source
(latest metadata: id, create_time, mentions); ``content`` and ``resources``
are unchanged from the last source - consumers should iterate
``batched_sources`` to access all media.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from lark_oapi.core.log import logger

from ..types import InboundMessage
from .types import MediaBatchConfig

MediaFlushHandler = Callable[[InboundMessage], Awaitable[None]]


def _kind_of(msg: InboundMessage) -> str:
    """Identify the media kind for batching. Empty string means non-media."""
    return msg.raw_content_type or ""


def _key_of(msg: InboundMessage) -> Tuple[str, str, str, str]:
    chat_id = msg.conversation.chat_id or ""
    kind = _kind_of(msg)
    reply_to = msg.reply.message_id if msg.reply else ""
    thread_id = getattr(msg.conversation, "thread_id", "") or ""
    return (chat_id, kind, reply_to, thread_id)


def _attach_sources_to_last(sources: List[InboundMessage]) -> InboundMessage:
    """Attach a media batch to the last source message and return that carrier.

    Use the last message as the carrier (latest metadata), attach all
    sources as ``batched_sources`` in arrival order.
    """
    if len(sources) == 1:
        return sources[0]
    last = sources[-1]
    last.batched_sources = list(sources)
    return last


@dataclass
class _Bucket:
    sources: List[InboundMessage] = field(default_factory=list)
    timer: Optional[asyncio.TimerHandle] = None


class MediaPipelineManager:
    """Per-key debounce + flush. Compatible with ``ChatPipelineManager``'s
    lifecycle: ``push(msg, handler)`` schedules; ``dispose()`` drains.
    """

    def __init__(
            self,
            config: MediaBatchConfig,
            loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._config = config
        self._loop = loop
        self._buckets: Dict[Tuple[str, str, str, str], _Bucket] = {}
        self._handler: Optional[MediaFlushHandler] = None

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def is_compatible(self, msg: InboundMessage) -> bool:
        kind = _kind_of(msg)
        return self._config.enabled and kind in self._config.compatible_kinds

    async def push(self, msg: InboundMessage, handler: MediaFlushHandler) -> None:
        """Add ``msg`` to its bucket. Flushes the bucket if max_items reached."""
        self._handler = handler
        key = _key_of(msg)
        bucket = self._buckets.setdefault(key, _Bucket())
        bucket.sources.append(msg)

        if len(bucket.sources) >= self._config.max_items:
            self._cancel_timer(bucket)
            await self._flush_bucket(key)
            return

        self._cancel_timer(bucket)
        bucket.timer = self._loop.call_later(
            self._config.delay_ms / 1000.0,
            lambda: self._spawn_flush(key),
        )

    def _spawn_flush(self, key: Tuple[str, str, str, str]) -> None:
        """Schedule ``_flush_bucket(key)`` with a logging done-callback so
        timer-driven flush failures do not vanish into a fire-and-forget task.
        """
        task = self._loop.create_task(self._flush_bucket(key))

        def _on_done(t: "asyncio.Task[Any]") -> None:
            if t.cancelled():
                return
            exc = t.exception()
            if exc is not None:
                logger.warning("media_pipeline: bucket flush failed: %s", exc)

        task.add_done_callback(_on_done)

    async def flush_incompatible_for(self, msg: InboundMessage) -> None:
        """Called when a non-compatible message arrives in a chat that has a
        pending bucket - flushes any bucket sharing the chat_id."""
        chat_id = msg.conversation.chat_id or ""
        keys_to_flush = [k for k in list(self._buckets.keys()) if k[0] == chat_id]
        for k in keys_to_flush:
            await self._flush_bucket(k)

    async def _flush_bucket(self, key: Tuple[str, str, str, str]) -> None:
        bucket = self._buckets.pop(key, None)
        if bucket is None or not bucket.sources:
            return
        self._cancel_timer(bucket)
        merged = _attach_sources_to_last(bucket.sources)
        if self._handler is not None:
            await self._handler(merged)

    def _cancel_timer(self, bucket: _Bucket) -> None:
        if bucket.timer is not None:
            try:
                bucket.timer.cancel()
            except Exception:
                pass
            bucket.timer = None

    async def dispose(self) -> None:
        """Flush any remaining buckets - call during channel shutdown."""
        for key in list(self._buckets.keys()):
            await self._flush_bucket(key)
