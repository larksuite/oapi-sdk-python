"""Coalescing task queue for streaming card updates.

Semantics: at any time, **at most one task runs and at most one task is
pending**. When a new task is enqueued while another is still pending
(queued but not yet started), the new one **replaces** the pending task —
only the most recent snapshot survives. If a task is currently running,
the new enqueue becomes the new pending; when the running task finishes,
it chains the pending task.

This matches the streaming-card use case where each enqueued task is a
snapshot of the current accumulated content. Only the latest snapshot
matters for user-visible state:

- ``MarkdownStreamController`` uses the server-sequenced element-update
  API (``update_card_element_content(card_id, elem_id, content, seq)``).
  The server orders updates by ``seq``; dropping an intermediate client-
  side task simply skips one round-trip — the next (latest) task still
  carries a higher seq and ends up winning.
- ``CardStreamController`` uses the non-sequenced ``patch_card`` API.
  Coalescing guarantees at most one HTTP is in flight at a time, so
  client-side serial execution is sufficient ordering.

**Intentional divergence from node-sdk**: node's ``UpdateQueue`` is a
strict FIFO that serializes *every* enqueued task. Python coalesces —
fewer HTTP calls under fast producers, no change to final state, but a
caller observing HTTP traffic will see fewer intermediate states in
Python than in node. Documented in the channel README.

Failure handling: a task exception is logged but NOT retried. The next
``enqueue`` naturally supersedes. Callers (e.g. ``MarkdownStreamController``)
should flush a final-state task in their terminal path so the user sees
complete content even if an intermediate update failed.
"""

import asyncio
from typing import Any, Awaitable, Callable, Optional

from lark_oapi.core.log import logger


class UpdateQueue:
    """Coalescing queue: at most 1 running + 1 pending task at any time."""

    def __init__(self) -> None:
        self._running: Optional[asyncio.Task] = None
        self._pending: Optional[Callable[[], Awaitable[Any]]] = None

    def enqueue(self, task: Callable[[], Awaitable[Any]]) -> None:
        """Schedule ``task``. If a task is pending (not yet started), it is
        silently replaced — only the latest survives.

        Returns nothing: callers cannot rely on the task running, since it
        may be superseded before start. Await :meth:`drain` to wait for
        the queue to quiesce.
        """
        self._pending = task
        if self._running is None or self._running.done():
            self._start_next()

    async def drain(self) -> None:
        """Wait until the queue is fully idle.

        Iterates because each running task, upon completion, may chain a
        pending task in its ``finally`` block — so we must re-check the
        tail state after awaiting.

        ``CancelledError`` propagates — a caller cancelling the drainer is
        a signal we should not absorb. Other exceptions are swallowed after
        being logged inside ``_runner`` so we can continue draining.
        """
        while self._running is not None and not self._running.done():
            try:
                await self._running
            except asyncio.CancelledError:
                raise
            except Exception:
                # Failures are already logged in _runner; keep draining.
                pass

    # ---- internals ----------------------------------------------------------
    def _start_next(self) -> None:
        """Claim `_pending` and kick off its task. Called from `enqueue` and
        from inside a completing task's `finally` block."""
        if self._pending is None:
            self._running = None
            return
        task = self._pending
        self._pending = None
        loop = asyncio.get_running_loop()

        async def _runner() -> None:
            try:
                await task()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning("UpdateQueue: task failed: %s", e)
            finally:
                # Chain the next pending (if any new enqueue happened while
                # we were running). Single-threaded asyncio means no race.
                self._start_next()

        self._running = loop.create_task(_runner())
