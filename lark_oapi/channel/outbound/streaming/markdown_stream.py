"""Markdown-centric streaming controller.

Pre-allocates a CardKit card with a single markdown element, then ticks the
element's content forward via sequenced ``update_card_element_content`` calls
so out-of-order HTTP delivery cannot rewind visible content. On producer error
the controller appends a terminated-footer, performs one final element update,
drains the queue, calls ``finish_streaming_card``, and re-raises.

Distinct from :class:`CardStreamController` (same directory), which accepts a
full card JSON per tick and backs that with generic ``patch_card``.
"""

from typing import Any, Awaitable, Callable, Dict, Optional

from lark_oapi.core.log import logger

from .merge_text import merge_streaming_text
from .throttle import Throttle
from .update_queue import UpdateQueue

ELEMENT_ID = "stream_md"
INITIAL_TEXT = "Thinking..."
TERMINATED_FOOTER = "\n\n— _(generation interrupted)_"

# Public type aliases for the 4 cardkit dependencies the controller needs.
CreateCardInstance = Callable[[Dict[str, Any]], Awaitable[str]]
SendCardByReference = Callable[..., Awaitable[Any]]
UpdateCardElementContent = Callable[[str, str, str, int], Awaitable[None]]
FinishStreamingCard = Callable[[str, int], Awaitable[None]]


class MarkdownStreamController:
    """User-facing controller passed to the producer closure.

    ``append()`` / ``set_content()`` are the only two methods the producer
    calls. Everything else is plumbing invoked from :class:`FeishuChannel`.
    """

    def __init__(
            self,
            *,
            to: str,
            receive_id_type: str,
            reply_to: Optional[str],
            reply_in_thread: Optional[bool],
            create_card_instance: CreateCardInstance,
            send_card_by_reference: SendCardByReference,
            update_card_element_content: UpdateCardElementContent,
            finish_streaming_card: FinishStreamingCard,
            reply_target_gone: str = "fresh",
            min_ms: int = 100,
            min_chars: int = 50,
            initial_text: str = INITIAL_TEXT,
            element_id: str = ELEMENT_ID,
    ) -> None:
        self._to = to
        self._rit = receive_id_type
        self._reply_to = reply_to
        self._reply_in_thread = reply_in_thread
        self._reply_target_gone = reply_target_gone
        self._create_card_instance = create_card_instance
        self._send_card_by_reference = send_card_by_reference
        self._update_card_element_content = update_card_element_content
        self._finish_streaming_card = finish_streaming_card
        self._initial_text = initial_text
        self._element_id = element_id

        self._card_id: Optional[str] = None
        self._message_id: str = ""
        self._sequence: int = 0
        self._content: str = ""

        self._queue = UpdateQueue()
        self._throttle = Throttle(
            min_ms=min_ms,
            min_chars=min_chars,
            on_fire=self._on_fire,
        )

    @property
    def message_id(self) -> str:
        return self._message_id

    @property
    def card_id(self) -> Optional[str]:
        return self._card_id

    # ---- producer-facing API -------------------------------------------------
    async def append(self, chunk: str) -> None:
        if not chunk:
            return
        await self._ensure_started()
        new_content = merge_streaming_text(self._content, chunk)
        delta = len(new_content) - len(self._content)
        self._content = new_content
        self._throttle.note(max(1, delta))

    async def set_content(self, full: str) -> None:
        await self._ensure_started()
        self._content = full or ""
        # Force immediate flush — mirrors node passing MAX_SAFE_INTEGER.
        self._throttle.flush_now()

    async def run(
            self, producer: Callable[["MarkdownStreamController"], Awaitable[None]]
    ) -> str:
        """Drive the producer; return the message_id.

        Success path: drain queue → ``finish_streaming_card``.
        Error path: append footer → push one final update → drain →
        ``finish_streaming_card`` → re-raise.
        """
        import asyncio as _asyncio

        try:
            await producer(self)
        except _asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning("markdown-stream: producer raised: %s", e)
            await self._fail_terminal()
            raise
        await self._complete_terminal()
        return self._message_id

    # ---- internals -----------------------------------------------------------
    async def _ensure_started(self) -> None:
        if self._card_id:
            return
        spec = {
            "schema": "2.0",
            "config": {"streaming_mode": True, "summary": {"content": ""}},
            "body": {
                "elements": [
                    {
                        "tag": "markdown",
                        "element_id": self._element_id,
                        "content": self._initial_text,
                    }
                ]
            },
        }
        self._card_id = await self._create_card_instance(spec)
        kwargs = {
            "receive_id_type": self._rit,
            "reply_to": self._reply_to,
            "reply_in_thread": self._reply_in_thread,
        }
        if self._reply_target_gone != "fresh":
            kwargs["reply_target_gone"] = self._reply_target_gone
        result = await self._send_card_by_reference(
            self._to,
            self._card_id,
            **kwargs,
        )
        self._message_id = getattr(result, "message_id", "") or ""

    def _on_fire(self) -> None:
        """Throttle callback: snapshot content, stamp seq, enqueue update."""
        if not self._card_id:
            return
        self._sequence += 1
        seq = self._sequence
        text = self._content or "..."
        card_id = self._card_id
        element_id = self._element_id
        self._queue.enqueue(
            lambda: self._update_card_element_content(card_id, element_id, text, seq)
        )

    async def _complete_terminal(self) -> None:
        # Flush any pending throttle work first.
        self._throttle.flush_now()
        await self._queue.drain()
        if self._card_id:
            self._sequence += 1
            try:
                await self._finish_streaming_card(self._card_id, self._sequence)
            except Exception as e:  # pragma: no cover
                logger.warning(
                    "markdown-stream: finish_streaming_card failed: %s", e
                )

    async def _fail_terminal(self) -> None:
        # If the card never got created (producer raised before first append),
        # synthesize it so the user at least sees the error footer.
        if not self._card_id:
            try:
                await self._ensure_started()
            except Exception:  # pragma: no cover
                return
        self._throttle.dispose()
        self._content = (self._content or "") + TERMINATED_FOOTER

        self._sequence += 1
        seq = self._sequence
        card_id = self._card_id
        element_id = self._element_id
        text = self._content
        self._queue.enqueue(
            lambda: self._update_card_element_content(card_id, element_id, text, seq)
        )
        await self._queue.drain()

        self._sequence += 1
        try:
            await self._finish_streaming_card(self._card_id, self._sequence)
        except Exception as e:  # pragma: no cover
            logger.warning(
                "markdown-stream: finish_streaming_card (error path) failed: %s", e
            )
