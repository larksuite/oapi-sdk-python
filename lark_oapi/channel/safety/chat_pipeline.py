"""Per-chat batch aggregation + serial handler execution.

Problem solved: a user firing rapid-fire messages ("help" / "write a" /
"quicksort") should be treated as ONE request, not three. Also: we must
never run two handlers concurrently for the same chat (races on shared
conversation state).

`ChatPipeline` owns both responsibilities for a given scope (usually chat_id
or file_token):

- **Batch**: incoming messages go into a buffer; a debounce timer fires after
  `delay_ms` (or `long_delay_ms` if accumulated chars ≥ `long_threshold_chars`).
  The timer, `max_messages`, and `max_chars` are three parallel flush triggers.
- **Serialize**: flushes are enqueued on a single task chain so a slow handler
  blocks later flushes in the same scope.

`ChatPipelineManager` is a keyed registry — one pipeline per chat_id.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional

from ..types import InboundMessage
from .types import ChatQueueConfig, TextBatchConfig

FlushHandler = Callable[[InboundMessage, List[InboundMessage]], Awaitable[None]]


def merge_batch(batch: List[InboundMessage]) -> InboundMessage:
    """Merge a batch of inbound messages into a single virtual message.

    The last message's metadata (id, sender, timestamps) wins; `content.text`
    is joined with `\\n\\n`; mentions and raw are unified.
    """
    if len(batch) == 1:
        return batch[0]
    last = batch[-1]
    texts: List[str] = []
    all_mentions = list(last.mentions or [])
    mentioned_all = False
    seen_mention_ids = set()
    for m in batch:
        content = m.content
        text = getattr(content, "text", "") or getattr(content, "title", "") or ""
        if text:
            texts.append(text)
        if m.mentioned_all:
            mentioned_all = True
        for mention in m.mentions or []:
            sig = mention.open_id or mention.user_id or mention.key
            if sig in seen_mention_ids:
                continue
            seen_mention_ids.add(sig)
            if mention not in all_mentions:
                all_mentions.append(mention)
    from ..types import InboundMessage as _IM, TextContent

    merged_content = last.content
    if isinstance(merged_content, TextContent) and texts:
        merged_content = TextContent(text="\n\n".join(texts), raw=merged_content.raw)
    merged = _IM(
        id=last.id,
        create_time=last.create_time,
        conversation=last.conversation,
        sender=last.sender,
        mentions=all_mentions,
        mentioned_all=mentioned_all or last.mentioned_all,
        reply=last.reply,
        content=merged_content,
        raw=last.raw,
    )
    return merged


class ChatPipeline:
    """Single-scope batch + serialize pipeline.

    Two modes:
    - `serial_only=False` (default): full batch + serialize. Used for messages.
    - `serial_only=True`: no batching; `run(task)` chains tasks FIFO. Used for
      cardAction / comment.
    """

    def __init__(
            self,
            scope: str,
            config: TextBatchConfig,
            loop: asyncio.AbstractEventLoop,
            *,
            serial_only: bool = False,
    ) -> None:
        self._scope = scope
        self._config = config
        self._loop = loop
        self._serial_only = serial_only

        self._buffer: List[InboundMessage] = []
        self._buffer_chars = 0
        self._timer: Optional[asyncio.TimerHandle] = None
        self._pending_handler: Optional[FlushHandler] = None
        self._tail: asyncio.Task = self._loop.create_task(self._noop())

    async def _noop(self) -> None:
        return None

    # ---- message batch path --------------------------------------------------
    def push(self, msg: InboundMessage, handler: FlushHandler) -> None:
        """Buffer a message and arm the debounce timer."""
        self._buffer.append(msg)
        text = getattr(msg.content, "text", "") or ""
        self._buffer_chars += len(text)
        if self._pending_handler is None:
            self._pending_handler = handler

        # Flush on caps
        if len(self._buffer) >= self._config.max_messages:
            self._cancel_timer()
            self._flush_async()
            return
        if self._buffer_chars >= self._config.max_chars:
            self._cancel_timer()
            self._flush_async()
            return

        # delayMs=0 or serial_only → immediate flush
        if self._config.delay_ms <= 0 or self._serial_only:
            self._cancel_timer()
            self._flush_async()
            return

        # Debounce: long messages get longer delay
        delay_ms = (
            self._config.long_delay_ms
            if self._buffer_chars >= self._config.long_threshold_chars
            else self._config.delay_ms
        )
        self._cancel_timer()
        self._timer = self._loop.call_later(delay_ms / 1000.0, self._flush_async)

    def _flush_async(self) -> None:
        if not self._buffer:
            return
        batch = self._buffer
        handler = self._pending_handler
        self._buffer = []
        self._buffer_chars = 0
        self._pending_handler = None
        if handler is None:
            return
        merged = merge_batch(batch)
        self._enqueue(lambda: handler(merged, batch))

    # ---- free-standing serialize path ---------------------------------------
    def run(self, task: Callable[[], Awaitable[Any]]) -> "asyncio.Future[Any]":
        """Chain a task onto the serial queue; returns a future for its result."""
        # Force any pending buffered batch to flush first
        if self._buffer:
            self._cancel_timer()
            self._flush_async()
        return self._enqueue(task)

    # ---- internals -----------------------------------------------------------
    def _enqueue(self, task: Callable[[], Awaitable[Any]]) -> "asyncio.Future[Any]":
        prev_tail = self._tail

        async def runner():
            # ``prev_tail`` is captured via closure. Without the ``nonlocal``
            # + explicit ``prev_tail = None`` below, each runner would hold a
            # reference to its predecessor for its entire lifetime, and a
            # long chat-history serialization chain (one runner per message
            # in a busy group) would keep every completed ancestor alive in
            # memory until the whole chain drains. Clearing the closure cell
            # as soon as we're past the await lets Python reap ancestors
            # eagerly.
            nonlocal prev_tail
            if prev_tail is not None:
                try:
                    await prev_tail
                except asyncio.CancelledError:
                    raise
                except Exception:  # prior task failure shouldn't block us
                    pass
            prev_tail = None  # drop the closure's grip on the previous task
            return await task()

        next_task = self._loop.create_task(runner())
        self._tail = next_task
        return next_task

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            try:
                self._timer.cancel()
            except Exception:  # pragma: no cover - defensive
                pass
            self._timer = None

    async def dispose(self) -> None:
        """Flush any buffered batch and wait for outstanding tasks."""
        self._cancel_timer()
        if self._buffer:
            self._flush_async()
        try:
            await self._tail
        except (asyncio.CancelledError, Exception):
            pass


class ChatPipelineManager:
    """Map of scope → ChatPipeline, lazily created."""

    def __init__(
            self,
            config: TextBatchConfig,
            loop: asyncio.AbstractEventLoop,
            queue_config: Optional[ChatQueueConfig] = None,
    ) -> None:
        self._config = config
        self._loop = loop
        self._queue_enabled = (queue_config or ChatQueueConfig()).enabled
        self._pipelines: Dict[str, ChatPipeline] = {}

    def push(self, scope: str, msg: InboundMessage, handler: FlushHandler) -> None:
        pipeline = self._pipelines.get(scope)
        if pipeline is None:
            pipeline = ChatPipeline(scope, self._config, self._loop, serial_only=False)
            self._pipelines[scope] = pipeline
        pipeline.push(msg, handler)

    def run(self, scope: str, task: Callable[[], Awaitable[Any]]) -> "asyncio.Future[Any]":
        pipeline = self._pipelines.get(scope)
        if pipeline is None:
            pipeline = ChatPipeline(scope, self._config, self._loop, serial_only=True)
            self._pipelines[scope] = pipeline
        return pipeline.run(task)

    async def dispose(self) -> None:
        for pipeline in list(self._pipelines.values()):
            await pipeline.dispose()
        self._pipelines.clear()

    @property
    def queue_enabled(self) -> bool:
        return self._queue_enabled
