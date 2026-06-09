"""User-driven card streaming.

The producer hands the controller a sequence of full card snapshots (or a
transform function). Unlike `MarkdownStreamController`, which manages content
string state, this variant gives the caller direct control over card JSON.

Use case: complex cards with progress bars, timestamps, dynamic elements.
"""

from typing import Any, Awaitable, Callable, Dict, Union

from lark_oapi.core.log import logger

from .throttle import Throttle
from .update_queue import UpdateQueue

STREAM_TERMINATED_FOOTER_ELEMENT = {
    "tag": "markdown",
    "content": "<font color='grey'>— generation interrupted</font>",
}

CardSnapshot = Union[Dict[str, Any], Callable[[Dict[str, Any]], Dict[str, Any]]]


class CardStreamController:
    def __init__(
            self,
            *,
            initial: Dict[str, Any],
            ensure_created: Callable[[Dict[str, Any]], Awaitable[str]],
            patch_card: Callable[[str, Dict[str, Any]], Awaitable[Any]],
            min_ms: int = 100,
            min_chars: int = 50,
    ) -> None:
        self._ensure_created = ensure_created
        self._patch_card = patch_card
        self._current: Dict[str, Any] = dict(initial)
        self._message_id = ""
        self._queue = UpdateQueue()
        self._throttle = Throttle(
            min_ms=min_ms, min_chars=min_chars, on_fire=self._on_fire,
        )

    @property
    def message_id(self) -> str:
        return self._message_id

    @property
    def current(self) -> Dict[str, Any]:
        return self._current

    async def update(self, next_card: CardSnapshot) -> None:
        await self._ensure_started()
        if callable(next_card):
            self._current = next_card(self._current)
        else:
            self._current = dict(next_card)
        # Approximate delta size for throttle — roll up serialized length
        import json as _json
        approx = len(_json.dumps(self._current, ensure_ascii=False))
        self._throttle.note(approx)

    async def run(self, producer: Callable[["CardStreamController"], Awaitable[None]]) -> str:
        import asyncio as _asyncio
        try:
            await producer(self)
        except _asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning("card stream: producer raised: %s", e)
            self._throttle.dispose()
            # Add a terminated footer element
            body = self._current.setdefault("body", {"elements": []})
            elements = body.setdefault("elements", [])
            elements.append(STREAM_TERMINATED_FOOTER_ELEMENT)
            await self._flush_final()
            raise
        self._throttle.flush_now()
        await self._queue.drain()
        return self._message_id

    # ---- internals -----------------------------------------------------------
    async def _ensure_started(self) -> None:
        if self._message_id:
            return
        self._message_id = await self._ensure_created(self._current)

    def _on_fire(self) -> None:
        if not self._message_id:
            return
        snapshot = dict(self._current)
        self._queue.enqueue(lambda: self._patch_card(self._message_id, snapshot))

    async def _flush_final(self) -> None:
        if not self._message_id:
            try:
                self._message_id = await self._ensure_created(self._current)
            except Exception:
                return
        snapshot = dict(self._current)
        self._queue.enqueue(lambda: self._patch_card(self._message_id, snapshot))
        await self._queue.drain()
