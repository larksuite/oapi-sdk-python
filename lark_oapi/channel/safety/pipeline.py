"""SafetyPipeline — three-tier entry point for events.

Exposes three push methods, each enforcing a different subset of the full
pipeline:

    push_message — full pipeline (stale / dedup / policy / lock / batch / queue)
    push_action  — dedup + lock + queue (cardAction / comment)
    push_light   — dedup only (reaction)

The pipeline owns a `PolicyGate`, `SeenCache`, `ProcessingLock`, and
`ChatPipelineManager`, composing them into a single call site.
"""

import asyncio
import inspect
from typing import Awaitable, Callable, Optional

from lark_oapi.core.cache import ICache
from lark_oapi.core.log import logger

from ..config import PolicyConfig
from ..types import InboundMessage
from .chat_pipeline import ChatPipelineManager
from .media_pipeline import MediaPipelineManager
from .policy_gate import PolicyGate
from .processing_lock import ProcessingLock
from .dedup_cache import SeenCache
from .stale_detector import DEFAULT_STALE_MS, is_stale
from .types import (
    ChatQueueConfig,
    DedupConfig,
    MediaBatchConfig,
    RejectEvent,
    RejectReason,
    TextBatchConfig,
)

MessageDispatch = Callable[[InboundMessage], Awaitable[None]]
OnReject = Callable[[RejectEvent], None]


class SafetyPipeline:
    """Facade that wires stale / dedup / policy / lock / batch / queue."""

    def __init__(
            self,
            *,
            loop: asyncio.AbstractEventLoop,
            on_message: MessageDispatch,
            on_reject: Optional[OnReject] = None,
            policy: Optional[PolicyConfig] = None,
            cache: Optional[ICache] = None,
            dedup_config: Optional[DedupConfig] = None,
            batch_config: Optional[TextBatchConfig] = None,
            media_batch_config: Optional[MediaBatchConfig] = None,
            queue_config: Optional[ChatQueueConfig] = None,
            stale_window_ms: int = DEFAULT_STALE_MS,
            processing_lock_ttl_ms: int = 5 * 60 * 1000,
            drop_self_sent: bool = True,
    ) -> None:
        self._loop = loop
        self._on_message = on_message
        self._on_reject = on_reject
        self._stale_window_ms = stale_window_ms
        self._drop_self_sent = drop_self_sent
        self._bot_open_id: Optional[str] = None

        dedup_config = dedup_config or DedupConfig()
        self._seen = SeenCache(
            cache=cache,
            ttl_seconds=dedup_config.ttl_seconds,
            max_entries=dedup_config.max_entries,
            sweep_seconds=dedup_config.sweep_seconds,
        )
        self._lock = ProcessingLock(ttl_ms=processing_lock_ttl_ms)
        self._policy = PolicyGate(policy or PolicyConfig())
        self._manager = ChatPipelineManager(
            config=batch_config or TextBatchConfig(),
            loop=loop,
            queue_config=queue_config or ChatQueueConfig(),
        )
        self._media = MediaPipelineManager(
            config=media_batch_config or MediaBatchConfig(),
            loop=loop,
        )

    # ---- public accessors ----------------------------------------------------
    @property
    def seen(self) -> SeenCache:
        return self._seen

    def set_bot_open_id(self, open_id: Optional[str]) -> None:
        self._bot_open_id = open_id
        self._policy.set_bot_open_id(open_id)

    def update_policy(self, **changes) -> None:
        self._policy.update_policy(**changes)

    def get_policy(self) -> PolicyConfig:
        return self._policy.get_policy()

    def _emit_reject(self, msg: InboundMessage, reason: "RejectReason") -> None:
        """Emit a :class:`RejectEvent` to the caller-supplied hook, if any.

        Kept internal because the event taxonomy is deliberately narrow; only
        :meth:`push_message` calls this. Swallows handler exceptions so a
        buggy reject callback can't break message processing.
        """
        if self._on_reject is None:
            return
        try:
            self._on_reject(RejectEvent(
                message_id=msg.id,
                chat_id=msg.conversation.chat_id,
                sender_id=msg.sender.open_id,
                reason=reason,
            ))
        except Exception as e:  # pragma: no cover
            logger.warning("safety: on_reject handler raised: %s", e)

    # ---- tier 1: full message pipeline ---------------------------------------
    async def push_message(self, msg: InboundMessage) -> None:
        """Run a message through the complete safety gauntlet."""
        # 1. Stale detector — emits RejectEvent(reason="stale") so subscribers
        #    can observe the drop.
        if is_stale(msg.create_time * 1000 if msg.create_time < 10 ** 12 else msg.create_time,
                    self._stale_window_ms):
            logger.debug("safety: stale drop message_id=%s", msg.id)
            self._emit_reject(msg, "stale")
            return

        # 2. Dedup (seen cache) — emits RejectEvent(reason="duplicate"); same
        #    rationale as the stale branch above.
        if await self._seen.has(msg.id):
            logger.debug("safety: dedup drop message_id=%s", msg.id)
            self._emit_reject(msg, "duplicate")
            return

        # 2.5 Self-sent filter — only when bot identity is known. Conservative:
        #     unknown identity skips the filter so legitimate user messages
        #     during startup aren't dropped.
        if (
                self._drop_self_sent
                and self._bot_open_id is not None
                and msg.sender.open_id == self._bot_open_id
        ):
            logger.debug("safety: self-sent drop message_id=%s", msg.id)
            self._emit_reject(msg, "self_sent")
            return

        # 3. Policy gate
        decision = self._policy.evaluate(msg)
        if not decision.allowed:
            if decision.reason is not None:
                self._emit_reject(msg, decision.reason)
            else:
                logger.debug("safety: policy drop message_id=%s reason=None", msg.id)
            return

        # 4. Processing lock
        if not self._lock.acquire(msg.id):
            logger.debug("safety: lock contention drop message_id=%s", msg.id)
            self._emit_reject(msg, "lock_contention")
            return

        # 5. Media batching takes precedence over the chat batch/queue path
        #    when the message is a compatible media kind. The chat queue is
        #    bypassed for batched media — the merged dispatch goes directly
        #    to the handler. Text and other kinds fall through to the
        #    existing batch+queue flow, but first we flush any pending media
        #    bucket on the same chat so order is preserved.
        if self._media.is_compatible(msg):
            await self._media.push(msg, self._media_flush_handler)
            return

        # Non-media (or non-compatible kind): flush any pending media bucket
        # in this chat first so order is preserved across the kind switch.
        if self._media.enabled:
            await self._media.flush_incompatible_for(msg)

        # 5a. batch + serialize (or direct if queue disabled)
        if self._manager.queue_enabled:
            self._manager.push(
                msg.conversation.chat_id or msg.id,
                msg,
                self._message_flush_handler,
            )
        else:
            await self._message_flush_handler(msg, [msg])

    async def _media_flush_handler(self, merged: InboundMessage) -> None:
        try:
            await _maybe_await(self._on_message(merged))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("safety: on_message handler raised: %s", e)
        finally:
            sources = merged.batched_sources or [merged]
            for m in sources:
                try:
                    await self._seen.add(m.id)
                except Exception:  # pragma: no cover
                    pass
                self._lock.release(m.id)

    async def _message_flush_handler(
            self, merged: InboundMessage, sources: "list[InboundMessage]"
    ) -> None:
        try:
            await _maybe_await(self._on_message(merged))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("safety: on_message handler raised: %s", e)
        finally:
            # Mark each source message as seen + release locks
            for m in sources:
                try:
                    await self._seen.add(m.id)
                except Exception:  # pragma: no cover
                    pass
                self._lock.release(m.id)

    # ---- tier 2: cardAction / comment (dedup + lock + serial) ----------------
    async def push_action(
            self,
            event_id: str,
            queue_scope: str,
            handler: Callable[[], Awaitable[None]],
    ) -> None:
        if await self._seen.has(event_id):
            logger.debug("safety: dedup drop action event_id=%s", event_id)
            return
        if not self._lock.acquire(event_id):
            logger.debug("safety: lock contention drop action event_id=%s", event_id)
            return

        async def runner() -> None:
            try:
                await _maybe_await(handler())
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.exception("safety: action handler raised: %s", e)
            finally:
                try:
                    await self._seen.add(event_id)
                except Exception:  # pragma: no cover
                    pass
                self._lock.release(event_id)

        self._manager.run(queue_scope, runner)

    # ---- tier 3: reaction (dedup only) ---------------------------------------
    async def push_light(
            self,
            event_id: str,
            handler: Callable[[], Awaitable[None]],
    ) -> None:
        if await self._seen.has(event_id):
            logger.debug("safety: dedup drop light event_id=%s", event_id)
            return
        try:
            await _maybe_await(handler())
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.exception("safety: light handler raised: %s", e)
        finally:
            try:
                await self._seen.add(event_id)
            except Exception:  # pragma: no cover
                pass

    async def dispose(self) -> None:
        await self._manager.dispose()
        await self._media.dispose()


async def _maybe_await(v):
    if inspect.isawaitable(v):
        return await v
    return v
