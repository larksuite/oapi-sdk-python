"""lark_oapi.channel.channel — the FeishuChannel capability layer.

Aligned 1:1 with node-sdk's ``FeishuChannel``. A single class owning lifecycle,
transport (WS / webhook), inbound normalization, safety pipeline, outbound
sender, and streaming.

The only event-registration API is node-style string events::

    channel.on("message", handler)      # handler(inbound: InboundMessage)
    channel.on("cardAction", handler)   # handler(event: CardActionEvent)
    channel.on("reaction", handler)     # handler(event: ReactionEvent)
    channel.on("botAdded", handler)     # handler(event: BotAddedEvent)
    channel.on("botLeave", handler)
    channel.on("messageRead", handler)
    channel.on("comment", handler)
    channel.on("reject", handler)       # handler(event: RejectEvent)
    channel.on("reconnecting", handler)
    channel.on("reconnected", handler)
    channel.on("error", handler)

For sending, streaming, message ops — use the channel methods directly
(``channel.send(...)``, ``channel.stream(...)``, ``channel.update_card(...)``,
etc). There are no typed-context hooks on event payloads — work with the
plain event data and call back into the channel.

Orchestration-only. Orthogonal concerns live next door:

- Input coercion      → :mod:`._coerce`
- Raw Lark API calls  → :mod:`._api_helpers`
- UAT device flow     → :mod:`.auth.uat_runner`
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Mapping, Optional, Set, Union

from lark_oapi.client import Client
from lark_oapi.core.enum import LogLevel
from lark_oapi.core.log import logger
from lark_oapi.event.callback.model.p2_card_action_trigger import (
    P2CardActionTrigger,
    P2CardActionTriggerResponse,
)
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws.client import Client as WSClient

from . import _api_helpers, _coerce
from .auth.device_flow import DeviceFlowClient
from .events import ChannelEventName
from lark_oapi.core.cache import ICache

from .auth.token_store import InMemoryTokenStore, TokenStore
from .auth.uat_runner import require_user_auth
from .bot_identity import BotIdentity, fetch_bot_identity
from .config import (
    ChannelConfig,
    InboundConfig,
    OutboundConfig,
    PolicyConfig,
    SafetyConfig,
    TransportConfig,
    UATConfig,
)
from .driver import LarkClientDriver
from .errors import FeishuChannelError, FeishuChannelErrorCode, OutboundSendError, SendError
from .identity import IdentityResolver, NameCache
from .normalize.comment import normalize_comment
from .normalize.dedup import Deduper, InMemoryDedupStore
from .normalize.pipeline import InboundPipeline, PipelineConfig, PipelineDeps
from .outbound.routing import infer_receive_id_type
from .outbound.sender import OutboundSender
from .outbound.streaming.card_stream import CardStreamController
from .outbound.streaming.markdown_stream import MarkdownStreamController
from .safety import RejectEvent, SafetyPipeline
from .types import (
    UAT,
    BotAddedEvent,
    BotLeaveEvent,
    CardActionEvent,
    CardActionPayload,
    ChatInfo,
    EventOperator,
    MediaSource,
    MessageReadEvent,
    OutboundCard,
    OutboundPost,
    OutboundText,
    ReactionEvent,
    SendResult,
)

EventHandler = Callable[..., Any]
Unsubscribe = Callable[[], None]


@dataclass
class _SentMessageContext:
    message_id: str
    chat_id: str
    chat_type: Optional[str] = None
    receive_id_type: Optional[str] = None


def _card_action_identity(action: Any) -> str:
    """Stable dedup fragment for a card action.

    Node-SDK aligned: different buttons on the same card click to different
    ``(tag, value)`` pairs, and those must dedup-distinctly; a genuine WS
    redelivery of the *same* click hashes identically and is suppressed.
    """
    tag = getattr(action, "tag", "") or ""
    value = getattr(action, "value", None)
    try:
        value_repr = json.dumps(value, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        value_repr = repr(value)
    return f"{tag}:{value_repr}"


# ---------------------------------------------------------------------------
# FeishuChannel
# ---------------------------------------------------------------------------


class FeishuChannel:
    """Single public entry point for the Feishu Channel capability layer.

    Construct with flat keyword arguments for the common case::

        channel = FeishuChannel(app_id="cli_xxx", app_secret="***")

    Or tune any of the five functional areas (``policy`` / ``safety`` /
    ``inbound`` / ``outbound`` / ``uat``) by passing a config dataclass::

        from lark_oapi.channel import (
            FeishuChannel, SafetyConfig, DedupConfig,
            OutboundConfig, RetryConfig,
        )

        channel = FeishuChannel(
            app_id="cli_xxx",
            app_secret="***",
            safety=SafetyConfig(dedup=DedupConfig(ttl_seconds=43_200)),
            outbound=OutboundConfig(retry=RetryConfig(max_attempts=5)),
        )

    For pre-built full configs, pass ``config=ChannelConfig(...)``; per-area
    kwargs override the fields they touch.
    """

    def __init__(
            self,
            *,
            app_id: Optional[str] = None,
            app_secret: Optional[str] = None,
            encrypt_key: Optional[str] = None,
            verification_token: Optional[str] = None,
            domain: Optional[str] = None,
            log_level: Optional[LogLevel] = None,
            transport: Optional[Union[str, TransportConfig]] = None,
            policy: Optional[PolicyConfig] = None,
            safety: Optional[SafetyConfig] = None,
            inbound: Optional[InboundConfig] = None,
            outbound: Optional[OutboundConfig] = None,
            uat: Optional[UATConfig] = None,
            token_store: Optional[TokenStore] = None,
            dedup_store: Any = None,
            safety_cache: Optional[ICache] = None,
            name_lookup: Optional[Callable[[List[str]], Any]] = None,
            config: Optional[ChannelConfig] = None,
    ) -> None:
        """Create a channel.

        ``dedup_store`` and ``safety_cache`` target **different** dedup
        layers — this is a deliberate split, not a redundancy:

        - ``dedup_store`` (:class:`~.normalize.dedup.DedupStore`) feeds the
          *pipeline* ``Deduper`` that catches webhook retries + WS reconnect
          backfill at the normalize step.
        - ``safety_cache`` (:class:`~lark_oapi.core.cache.ICache`, usually
          Redis-backed) feeds the *safety* ``SeenCache`` used by
          :class:`SafetyPipeline` for pre-dispatch dedup + (with an atomic
          SETNX implementation) cross-process coherence.

        Both default to in-memory when left as ``None``.
        """
        cfg = config if config is not None else ChannelConfig()
        if app_id is not None:
            cfg.app_id = app_id
        if app_secret is not None:
            cfg.app_secret = app_secret
        if encrypt_key is not None:
            cfg.encrypt_key = encrypt_key
        if verification_token is not None:
            cfg.verification_token = verification_token
        if domain is not None:
            cfg.domain = domain
        if log_level is not None:
            cfg.log_level = log_level
        if policy is not None:
            cfg.policy = policy
        if safety is not None:
            cfg.safety = safety
        if inbound is not None:
            cfg.inbound = inbound
        if outbound is not None:
            cfg.outbound = outbound
        if uat is not None:
            cfg.uat = uat
        if transport is not None:
            if isinstance(transport, str):
                if transport not in ("ws", "webhook"):
                    raise ValueError(
                        f"transport must be 'ws' or 'webhook', got {transport!r}"
                    )
                cfg.transport = TransportConfig(kind=transport)
            else:
                cfg.transport = transport
        if not cfg.app_id or not cfg.app_secret:
            raise ValueError("FeishuChannel requires app_id and app_secret")

        self._config = cfg
        self._safety_cache = safety_cache

        self._client = (
            Client.builder()
            .app_id(cfg.app_id)
            .app_secret(cfg.app_secret)
            .domain(cfg.domain)
            .log_level(cfg.log_level)
            .build()
        )
        # Mark all HTTP requests originating from this capability layer with a
        # bare ``channel`` token in the User-Agent so the backend can attribute
        # traffic to the channel SDK. Mirrors node-sdk's ``extraUaTags``.
        if self._client._config is not None:
            self._client._config.extra_ua_tags = ["channel"]
        self._driver = LarkClientDriver(self._client)
        self._sender = OutboundSender(
            driver=self._driver.send_driver(),
            config=cfg.outbound,
            on_success=self._track_sent_message,
        )

        self._dedup_store = dedup_store or InMemoryDedupStore(
            max_entries=cfg.safety.dedup.max_entries
        )
        self._deduper = Deduper(
            store=self._dedup_store,
            ttl_seconds=cfg.safety.dedup.ttl_seconds,
            enabled=cfg.safety.dedup.enabled,
        )

        self._identity_resolver = IdentityResolver(
            lookup=name_lookup
                   or (lambda ids: _api_helpers.default_name_lookup(self._client, ids)),
            cache=NameCache(cfg.inbound.name_cache),
        )

        self._token_store: TokenStore = token_store or InMemoryTokenStore()
        self._device_flow = DeviceFlowClient(
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            domain=cfg.domain,
        )

        self._pipeline = InboundPipeline(
            cfg=PipelineConfig(
                inbound=cfg.inbound, account_id=cfg.app_id
            ),
            deps=PipelineDeps(
                fetch_message=self._fetch_message_payload,
                resolve_names=self._identity_resolver.resolve_names,
                resolve_identity=self._identity_resolver.resolve,
            ),
            deduper=self._deduper,
        )

        self._safety: Optional[SafetyPipeline] = None

        # Node-style string-event handlers. Multiple handlers per event name
        # are appended in registration order; `_invoke` iterates them all.
        self._handlers: Dict[str, List[EventHandler]] = {}

        self._dispatcher: Optional[EventDispatcherHandler] = None
        self._ws_client: Optional[WSClient] = None

        self._bot_identity: Optional[BotIdentity] = None
        self._bot_open_id: Optional[str] = None
        # Guards reads / writes to ``_bot_identity`` + ``_bot_open_id`` +
        # ``_safety.set_bot_open_id`` so the initial fetch, an explicit
        # ``await resolve_bot_identity()``, and the background retry loop
        # can't leave the two fields in a half-updated state when a reader
        # on the bg loop is inspecting them.
        self._bot_identity_lock = threading.Lock()

        self._sent_messages: "OrderedDict[str, float]" = OrderedDict()
        self._sent_message_context: "OrderedDict[str, _SentMessageContext]" = OrderedDict()
        self._sent_messages_max = 2048
        self._start_future: Optional[asyncio.Future] = None

        self._bg_loop: Optional[asyncio.AbstractEventLoop] = None
        self._bg_thread: Optional[threading.Thread] = None
        # Guards start/stop of the bg loop so concurrent connect() calls can't
        # spawn two loops + two threads.
        self._bg_lock = threading.Lock()

        # References to Futures returned by `schedule(...)` — kept alive so
        # exceptions surface (done callback logs) and so shutdown can drain /
        # cancel in-flight work.
        self._bg_tasks: Set[concurrent.futures.Future] = set()
        self._bg_tasks_lock = threading.Lock()

        self._shutdown = threading.Event()
        self._stop_requested = False
        self._started = False
        self._lifecycle_lock = threading.Lock()
        self._lifecycle_generation = 0
        self._background_generation = 0
        # Lazy-init: asyncio.Event() in older Python (<3.10) requires a
        # running loop; create on first access from a coroutine context.
        self._ready_event: Optional[asyncio.Event] = None
        self._ready_flag: bool = False

    # ------------------------------------------------------------------
    # Event registration
    # ------------------------------------------------------------------
    def on(
            self,
            name_or_map: Union[ChannelEventName, Dict[ChannelEventName, EventHandler]],
            handler: Optional[EventHandler] = None,
    ) -> Unsubscribe:
        """Register an event handler.

        Accepts ``on(event_name, handler)`` or ``on({event_name: handler})``.
        Returns an unsubscribe callable that pops exactly this handler from
        the list.

        ``name_or_map`` is type-hinted with :data:`.events.ChannelEventName`
        so static type checkers catch typos (e.g. ``"messageReceive"`` vs
        the correct ``"message"``). At runtime, unknown names produce a
        warning log but do not raise — several historical aliases are still
        accepted via :mod:`._coerce`.
        """
        if isinstance(name_or_map, dict):
            subs = [self._register_single(k, v) for k, v in name_or_map.items() if v]
            return lambda: [u() for u in subs]
        if handler is None:
            raise TypeError(
                "FeishuChannel.on expects a handler when called with an event name"
            )
        return self._register_single(name_or_map, handler)

    def _register_single(self, name: str, handler: EventHandler) -> Unsubscribe:
        normalized = _coerce.normalize_event_name(name)
        if normalized not in _coerce.VALID_EVENTS:
            logger.warning("FeishuChannel.on: unknown event %r", name)
        self._handlers.setdefault(normalized, []).append(handler)

        def unsubscribe() -> None:
            lst = self._handlers.get(normalized)
            if not lst:
                return
            try:
                lst.remove(handler)
            except ValueError:
                return
            if not lst:
                self._handlers.pop(normalized, None)

        return unsubscribe

    async def _invoke(self, name: str, *args) -> None:
        handlers = self._handlers.get(_coerce.normalize_event_name(name))
        if not handlers:
            return
        # Iterate a snapshot so handlers unsubscribing themselves mid-invoke
        # don't mutate the list we're walking.
        for handler in list(handlers):
            try:
                result = handler(*args)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logger.exception(
                    "FeishuChannel: handler for %r raised: %s", name, e
                )
                for err in self._handlers.get("error", []):
                    try:
                        res = err(e)
                        if inspect.isawaitable(res):
                            await res
                    except Exception:  # pragma: no cover
                        pass

    # ------------------------------------------------------------------
    # Properties / escape hatches
    # ------------------------------------------------------------------
    @property
    def client(self) -> Client:
        """The underlying OpenAPI ``Client``."""
        return self._client

    @property
    def ws_client(self) -> Optional[WSClient]:
        """The WebSocket client if the channel was started in ``ws`` mode."""
        return self._ws_client

    @property
    def bot_identity(self) -> Optional[BotIdentity]:
        """Currently-resolved bot identity, or ``None`` if not yet fetched.

        Read under the same lock that guards writes so callers never observe
        a half-updated state (``_bot_identity`` fresh but ``_bot_open_id``
        stale or vice-versa).
        """
        with self._bot_identity_lock:
            return self._bot_identity

    @property
    def config(self) -> ChannelConfig:
        return self._config

    @property
    def safety(self) -> Optional[SafetyPipeline]:
        return self._safety

    @property
    def sender(self) -> OutboundSender:
        return self._sender

    @property
    def driver(self) -> LarkClientDriver:
        return self._driver

    @property
    def dispatcher(self) -> EventDispatcherHandler:
        if self._dispatcher is None:
            self._dispatcher = self._build_dispatcher()
        return self._dispatcher

    async def handle_webhook_request(
            self,
            headers: "Mapping[str, str]",
            body: bytes,
    ) -> "tuple[int, bytes]":
        """Process a single inbound webhook request.

        This is the framework-agnostic entry point — wrap with aiohttp /
        starlette / fastapi / your favorite web layer. The SDK does not ship
        a built-in webhook server; rate limiting, anomaly tracking, and IP
        allowlisting are deployment concerns that live in your service.

        Behavior:

        - Decrypts the body using ``encrypt_key`` (if configured).
        - Verifies the request via ``verification_token`` (if configured).
        - Verifies the request signature against the headers (when
          ``encrypt_key`` is set, the dispatcher checks
          ``X-Lark-Request-Timestamp`` / ``X-Lark-Request-Nonce`` /
          ``X-Lark-Signature``).
        - Routes the event to your registered ``channel.on(...)`` handlers.

        Args:
            headers: HTTP request headers (typically a dict-like; case
                sensitivity follows your framework's conventions).
            body: Raw HTTP request body bytes.

        Returns:
            ``(status_code, response_body_bytes)`` — write the body straight
            back to your HTTP response.

        Raises:
            FeishuChannelError(NOT_CONNECTED): When called before ``start()``.
                The dispatcher converts bad-token / signature failures to a
                500 response body itself; this method does not raise on those.
        """
        if self._dispatcher is None:
            raise FeishuChannelError(
                FeishuChannelErrorCode.NOT_CONNECTED,
                "handle_webhook_request called before start() — dispatcher missing",
            )

        from lark_oapi.core.model.raw_request import RawRequest
        req = RawRequest()
        req.uri = "/webhook"
        req.headers = dict(headers) if headers else {}
        req.body = body

        # The dispatcher's `do` is sync; offload so we don't block the
        # caller's event loop on signature verification + JSON parse.
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(None, self._dispatcher.do, req)
        status = getattr(resp, "status_code", 200) or 200
        content = getattr(resp, "content", b"")
        if isinstance(content, str):
            content = content.encode("utf-8")
        if not isinstance(content, (bytes, bytearray)):
            content = bytes(content) if content is not None else b""
        return status, content

    def get_policy(self) -> PolicyConfig:
        return self._config.policy

    def update_policy(self, **changes) -> None:
        if self._safety is not None:
            self._safety.update_policy(**changes)
        for k, v in changes.items():
            if hasattr(self._config.policy, k):
                setattr(self._config.policy, k, v)

    # ------------------------------------------------------------------
    # Readiness
    # ------------------------------------------------------------------
    @property
    def is_ready(self) -> bool:
        """True after start() has fully initialized.

        Specifically: WS connect has succeeded (or webhook dispatcher is
        constructed), bot identity is resolved (or its retry loop is running),
        and the safety pipeline is initialized. Events received before this
        point are NOT dispatched to user handlers — they are dropped (the
        WS-reconnect backfill or webhook retries cover startup-window losses).
        """
        return self._ready_flag

    async def wait_ready(self, *, timeout: Optional[float] = None) -> None:
        """Block until is_ready turns True. Raises asyncio.TimeoutError on timeout."""
        ev = self._ensure_ready_event()
        if self._ready_flag:
            return
        if timeout is None:
            await ev.wait()
            return
        await asyncio.wait_for(ev.wait(), timeout=timeout)

    def _mark_ready(self) -> None:
        """Internal: flip the readiness event. Called at the end of start()
        after WS connect, bot identity fetch, and safety pipeline init.
        Idempotent.
        """
        self._ready_flag = True
        ev = self._ready_event
        if ev is not None:
            try:
                ev.set()
            except Exception:  # pragma: no cover
                pass

    def _ensure_ready_event(self) -> "asyncio.Event":
        """Lazily create the asyncio.Event so we don't need a running loop in __init__."""
        if self._ready_event is None:
            self._ready_event = asyncio.Event()
            if self._ready_flag:
                self._ready_event.set()
        return self._ready_event

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def connect(self) -> None:
        """Idempotent. Blocks until WS connects or Webhook dispatcher is ready."""
        if getattr(self, "_started", False):
            return
        await asyncio.get_running_loop().run_in_executor(None, self.start)

    async def start_background(self, *, timeout: Optional[float] = 30.0) -> None:
        """Start transport in the background and return once it is ready.

        ``connect()`` keeps the historical foreground/blocking WebSocket
        behavior. Async applications that need startup to continue after the
        WebSocket handshake should use this method instead.
        """
        if self._ready_flag:
            return
        loop = asyncio.get_running_loop()
        if self._start_future is None or self._start_future.done():
            with self._lifecycle_lock:
                self._stop_requested = False
                self._background_generation += 1
                background_generation = self._background_generation
            self._start_future = loop.run_in_executor(None, self.start)
        else:
            with self._lifecycle_lock:
                background_generation = self._background_generation
        await self._wait_background_start_ready(
            timeout=timeout,
            generation=background_generation,
        )

    async def connect_until_ready(self, *, timeout: Optional[float] = 30.0) -> None:
        """Alias for :meth:`start_background` with explicit ready semantics."""
        await self.start_background(timeout=timeout)

    async def stop_background(self) -> None:
        """Stop a channel started by :meth:`start_background`.

        This is equivalent to :meth:`disconnect`; it is provided as the
        lifecycle counterpart to ``start_background``.
        """
        await self.disconnect()

    async def _wait_background_start_ready(
            self,
            *,
            timeout: Optional[float],
            generation: int,
    ) -> None:
        loop = asyncio.get_running_loop()
        deadline = None if timeout is None else loop.time() + timeout
        while True:
            if self._ready_flag:
                return
            if generation != self._background_generation:
                return
            if self._stop_requested:
                return
            fut = self._start_future
            if fut is None:
                await asyncio.sleep(0.05)
                continue
            if fut is not None and fut.done():
                if fut.cancelled():
                    if generation != self._background_generation or self._stop_requested:
                        return
                    raise FeishuChannelError(
                        FeishuChannelErrorCode.NOT_CONNECTED,
                        "Channel background start was cancelled",
                    )
                exc = fut.exception()
                if exc is not None:
                    raise exc
                if self._ready_flag or self._config.transport.kind == "webhook":
                    return
                raise FeishuChannelError(
                    FeishuChannelErrorCode.NOT_CONNECTED,
                    "Channel start exited before transport became ready",
                )
            ws = self._ws_client
            if ws is not None and getattr(ws, "_conn", None) is not None:
                self._mark_ready()
                return
            if deadline is not None and loop.time() >= deadline:
                self.stop()
                raise FeishuChannelError(
                    FeishuChannelErrorCode.NOT_CONNECTED,
                    "Timed out waiting for channel transport readiness",
                )
            await asyncio.sleep(0.05)

    async def disconnect(self) -> None:
        """Gracefully drain safety pipeline batches + stop the WS loop."""
        if self._safety is not None:
            try:
                await self._safety.dispose()
            except Exception:  # pragma: no cover
                pass
        self.stop()

    def start(self) -> None:
        """Start WS (blocking) or return after initializing Webhook dispatcher.

        Transport-level failures (bad credentials, network unreachable, TLS
        handshake failure, ...) are wrapped into
        :class:`FeishuChannelError(NOT_CONNECTED)` with the original
        exception chained via ``__cause__``. This gives callers a stable,
        ``code``-bearing exception to match on instead of whatever raw
        exception the underlying transport happens to raise (e.g.
        ``lark_oapi.ws.client.ClientException`` whose ``.code`` is an int).
        """
        if self._started:
            return
        with self._lifecycle_lock:
            self._lifecycle_generation += 1
            generation = self._lifecycle_generation
            self._stop_requested = False
            self._started = True
        self._ensure_bg_loop()
        self._fetch_bot_identity_sync()
        self._dispatcher = self._build_dispatcher()
        if self._config.transport.kind == "webhook":
            with self._lifecycle_lock:
                if not self._is_active_start(generation):
                    return
                logger.info(
                    "FeishuChannel: webhook mode ready — pass `dispatcher` to your HTTP adaptor"
                )
                self._mark_ready()
            return
        with self._lifecycle_lock:
            if not self._is_active_start(generation):
                return
            self._ws_client = WSClient(
                self._config.app_id,
                self._config.app_secret,
                log_level=self._config.log_level,
                event_handler=self._dispatcher,
                domain=self._config.domain,
                auto_reconnect=self._config.transport.auto_reconnect,
                extra_ua_tags=["channel"],
                headers=self._config.transport.headers,
            )
            # Wire transport-level reconnect events to the public ``on()`` bus so
            # callers registering ``on("reconnecting", ...) / on("reconnected", ...)``
            # actually observe them.
            self._ws_client.on_reconnecting = self._notify_reconnecting
            self._ws_client.on_reconnected = self._notify_reconnected
        try:
            self._ws_client.start()
        except FeishuChannelError:
            # Already the right shape; just reset started so caller can retry.
            self._finish_failed_start(generation)
            raise
        except Exception as e:
            if not self._is_active_start(generation):
                return
            # Anything else (ws client's ClientException, timeouts, DNS, ...)
            # → typed NOT_CONNECTED so callers can ``except FeishuChannelError
            # as err: if err.code == FeishuChannelErrorCode.NOT_CONNECTED``.
            self._finish_failed_start(generation)
            raise FeishuChannelError(
                FeishuChannelErrorCode.NOT_CONNECTED,
                f"WebSocket connect failed: {e}",
            ) from e
        with self._lifecycle_lock:
            if not self._is_active_start(generation):
                return
            self._mark_ready()

    def _is_active_start(self, generation: int) -> bool:
        if (
                generation != self._lifecycle_generation
                or self._shutdown.is_set()
                or self._stop_requested
        ):
            if generation == self._lifecycle_generation:
                self._started = False
            return False
        return True

    def _finish_failed_start(self, generation: int) -> None:
        with self._lifecycle_lock:
            if generation == self._lifecycle_generation:
                self._started = False

    def stop(self, *, join_timeout: float = 5.0) -> None:
        """Tear down everything the channel owns.

        Safe to call from any thread, idempotent. Steps:

        1. Signal shutdown (sets ``self._shutdown``).
        2. Stop the WS client if one was created.
        3. Cancel in-flight futures returned from :meth:`schedule`.
        4. Run ``DeviceFlowClient.close()`` on the bg loop to release httpx.
        5. Stop the bg loop and join its thread.
        """
        if self._shutdown.is_set():
            return
        self._shutdown.set()
        if self._start_future is not None:
            try:
                self._start_future.cancel()
            except Exception:  # pragma: no cover
                pass

        # 1. Stop WS client (best-effort; some builds don't expose stop()).
        with self._lifecycle_lock:
            self._background_generation += 1
            self._lifecycle_generation += 1
            self._stop_requested = True
            ws = self._ws_client
        if ws is not None:
            stopped = False
            for meth in ("stop", "close", "disconnect"):
                fn = getattr(ws, meth, None)
                if callable(fn):
                    try:
                        fn()
                    except Exception as e:  # pragma: no cover
                        logger.warning("FeishuChannel.stop: ws.%s raised: %s", meth, e)
                    stopped = True
                    break
            if not stopped:
                self._stop_private_ws_client(ws)

        # 2. Cancel scheduled futures.
        with self._bg_tasks_lock:
            pending = list(self._bg_tasks)
        for fut in pending:
            try:
                fut.cancel()
            except Exception:  # pragma: no cover
                pass

        # 3. Close httpx client inside device_flow via the bg loop (if up).
        if self._bg_loop is not None and self._bg_loop.is_running():
            try:
                close_fut = asyncio.run_coroutine_threadsafe(
                    self._device_flow.close(), self._bg_loop
                )
                try:
                    close_fut.result(timeout=2.0)
                except (concurrent.futures.TimeoutError, Exception) as e:  # pragma: no cover
                    logger.warning("FeishuChannel.stop: device_flow.close timed out: %s", e)
            except RuntimeError:  # pragma: no cover - loop closed between checks
                pass

        # 4. Stop the bg loop + join thread.
        loop = self._bg_loop
        thread = self._bg_thread
        if loop is not None:
            try:
                loop.call_soon_threadsafe(loop.stop)
            except RuntimeError:  # pragma: no cover - already stopped
                pass
        if thread is not None and thread.is_alive():
            thread.join(timeout=join_timeout)
            if thread.is_alive():  # pragma: no cover
                logger.warning(
                    "FeishuChannel.stop: bg thread did not exit within %.1fs",
                    join_timeout,
                )
        self._bg_loop = None
        self._bg_thread = None
        self._ws_client = None
        self._start_future = None

        # Allow a subsequent connect()/start() to actually run. Without
        # clearing these two flags, a channel that was stopped would be
        # permanently inert — any future connect() would short-circuit on
        # ``self._started`` and ``_ensure_bg_loop`` would refuse on the
        # persisted ``_shutdown``.
        self._shutdown.clear()
        self._started = False
        self._ready_flag = False
        if self._ready_event is not None:
            try:
                self._ready_event.clear()
            except Exception:  # pragma: no cover
                pass
        with self._bg_tasks_lock:
            self._bg_tasks.clear()

    def _stop_private_ws_client(self, ws: Any) -> None:
        disconnect = getattr(ws, "_disconnect", None)
        try:
            from lark_oapi.ws import client as ws_client_module

            ws_loop = getattr(ws_client_module, "loop", None)
            if callable(disconnect) and ws_loop is not None:
                if ws_loop.is_running():
                    try:
                        running_loop = asyncio.get_running_loop()
                    except RuntimeError:
                        running_loop = None
                    if running_loop is ws_loop:
                        ws_loop.create_task(disconnect())
                    else:
                        fut = asyncio.run_coroutine_threadsafe(disconnect(), ws_loop)
                        try:
                            fut.result(timeout=2.0)
                        except Exception as e:  # pragma: no cover
                            logger.warning("FeishuChannel.stop: ws._disconnect timed out: %s", e)
                elif not ws_loop.is_closed():
                    ws_loop.run_until_complete(disconnect())
            if ws_loop is not None and ws_loop.is_running():
                ws_loop.call_soon_threadsafe(ws_loop.stop)
        except Exception as e:  # pragma: no cover
            logger.warning("FeishuChannel.stop: private ws shutdown raised: %s", e)

    def schedule(self, coro) -> "concurrent.futures.Future":
        """Submit a coroutine to the background loop; safe from any thread.

        The returned Future is also tracked internally so exceptions surface
        via a logging done-callback (no more fire-and-forget) and so
        :meth:`stop` can cancel in-flight work. Callers may still ignore the
        return value.
        """
        self._ensure_bg_loop()
        if self._bg_loop is None:
            raise RuntimeError("FeishuChannel: background loop is not running")
        try:
            fut = asyncio.run_coroutine_threadsafe(coro, self._bg_loop)
        except RuntimeError as e:  # pragma: no cover - loop closed
            logger.warning("FeishuChannel: schedule failed: %s", e)
            raise
        with self._bg_tasks_lock:
            self._bg_tasks.add(fut)

        def _done(f: "concurrent.futures.Future") -> None:
            with self._bg_tasks_lock:
                self._bg_tasks.discard(f)
            if f.cancelled():
                return
            exc = f.exception()
            if exc is not None:
                logger.exception(
                    "FeishuChannel.schedule: background task raised: %s", exc,
                    exc_info=exc,
                )

        fut.add_done_callback(_done)
        return fut

    # Backoff schedule used by :meth:`_start_bot_identity_retry_loop`.
    # Covers roughly 1h 15m of retries: 10s, 30s, 2m, 10m, 1h. After that we
    # give up and log once at ERROR; a caller can always invoke
    # :meth:`resolve_bot_identity` manually to try again.
    _BOT_IDENTITY_RETRY_DELAYS_S = (10, 30, 120, 600, 3600)

    def _store_bot_identity(self, identity: Optional[BotIdentity]) -> None:
        """Atomically swap in a fresh bot identity + propagate to safety."""
        with self._bot_identity_lock:
            self._bot_identity = identity
            self._bot_open_id = identity.open_id if identity is not None else None
            safety = self._safety
            if safety is not None and identity is not None:
                safety.set_bot_open_id(identity.open_id)

    async def resolve_bot_identity(self) -> Optional[BotIdentity]:
        """Fetch the bot identity + publish it to readers under a lock.

        Safe to call from any loop. Returns the resolved identity (or None if
        the upstream call failed — callers that need the identity should
        react to None by retrying later).
        """
        identity = await fetch_bot_identity(self._client.config)
        if identity is not None:
            self._store_bot_identity(identity)
        return identity

    def _fetch_bot_identity_sync(self) -> None:
        if self._bg_loop is None:
            raise RuntimeError("FeishuChannel: background loop is not running")
        fut = asyncio.run_coroutine_threadsafe(
            fetch_bot_identity(self._client.config), self._bg_loop
        )
        try:
            identity = fut.result(timeout=10)
        except Exception as e:
            logger.warning("FeishuChannel: bot identity fetch failed: %s", e)
            identity = None
        if identity is None:
            # A transient network hiccup at startup can leave group ``@Bot``
            # detection unavailable until identity resolves. Schedule a
            # background backoff retry loop instead of treating startup lookup
            # as the only chance to populate ``_bot_open_id``.
            logger.warning(
                "FeishuChannel: bot identity unresolved on startup — "
                "scheduling background retry (group @Bot detection will "
                "remain off until resolved)"
            )
            self._start_bot_identity_retry_loop()
            return
        self._store_bot_identity(identity)
        logger.info(
            "FeishuChannel: bot identity resolved — open_id=%s name=%s",
            identity.open_id, identity.name,
        )

    def _start_bot_identity_retry_loop(self) -> None:
        """Schedule a backoff retry task on the bg loop."""
        if self._bg_loop is None:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                self._bot_identity_retry_loop(), self._bg_loop
            )
        except RuntimeError:  # pragma: no cover - loop already stopped
            pass

    async def _bot_identity_retry_loop(self) -> None:
        """Retry ``fetch_bot_identity`` on a backoff schedule until it
        succeeds, shutdown fires, or we exhaust the delay table."""
        for delay_s in self._BOT_IDENTITY_RETRY_DELAYS_S:
            try:
                await asyncio.sleep(delay_s)
            except asyncio.CancelledError:
                raise
            if self._shutdown.is_set():
                return
            # Someone else (manual resolve_bot_identity call) may have
            # already filled it in — bail out without a pointless fetch.
            with self._bot_identity_lock:
                if self._bot_identity is not None:
                    return
            try:
                identity = await fetch_bot_identity(self._client.config)
            except Exception as e:
                logger.warning(
                    "FeishuChannel: bot identity retry failed (delay=%ds): %s",
                    delay_s, e,
                )
                continue
            if identity is not None:
                self._store_bot_identity(identity)
                logger.info(
                    "FeishuChannel: bot identity resolved on retry — open_id=%s",
                    identity.open_id,
                )
                return
        logger.error(
            "FeishuChannel: bot identity still unresolved after all retries — "
            "group @Bot detection is disabled for this process; call "
            "channel.resolve_bot_identity() manually to try again"
        )

    def _ensure_bg_loop(self) -> None:
        # Double-checked locking: the outer check avoids the lock in the hot
        # path, the inner check prevents a race between two concurrent
        # callers both seeing None and each spawning their own loop+thread.
        if self._bg_loop is not None:
            return
        with self._bg_lock:
            if self._bg_loop is not None:
                return
            if self._shutdown.is_set():
                raise RuntimeError(
                    "FeishuChannel._ensure_bg_loop: channel is shutting down"
                )
            loop = asyncio.new_event_loop()

            def _runner() -> None:
                asyncio.set_event_loop(loop)
                try:
                    loop.run_forever()
                finally:
                    try:
                        loop.close()
                    except Exception:  # pragma: no cover
                        pass

            t = threading.Thread(target=_runner, name="lark-channel-bg", daemon=True)
            t.start()
            self._bg_loop = loop
            self._bg_thread = t

        async def _build_safety():
            safety_cfg = self._config.safety
            return SafetyPipeline(
                loop=self._bg_loop,
                on_message=self._dispatch_inbound_to_user,
                on_reject=self._emit_reject,
                policy=self._config.policy,
                # Safety-layer dedup cache (ICache, usually Redis) — wired
                # explicitly from the constructor kwarg, independent of the
                # pipeline-layer DedupStore that feeds `self._deduper`.
                cache=self._safety_cache,
                dedup_config=safety_cfg.dedup,
                batch_config=safety_cfg.text_batch,
                media_batch_config=safety_cfg.media_batch,
                queue_config=safety_cfg.chat_queue,
                stale_window_ms=safety_cfg.stale_message_window_ms,
                drop_self_sent=self._config.inbound.drop_self_sent,
            )

        fut = asyncio.run_coroutine_threadsafe(_build_safety(), self._bg_loop)
        self._safety = fut.result(timeout=5)
        with self._bot_identity_lock:
            open_id = self._bot_open_id
        if open_id:
            self._safety.set_bot_open_id(open_id)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def _build_dispatcher(self) -> EventDispatcherHandler:
        b = EventDispatcherHandler.builder(
            self._config.encrypt_key or "",
            self._config.verification_token or "",
            self._config.log_level,
        )
        b = b.register_p2_im_message_receive_v1(self._on_p2_im_message_receive_v1)
        b = b.register_p2_card_action_trigger(self._on_p2_card_action_trigger)
        for register, handler in (
                ("register_p2_im_message_reaction_created_v1", self._on_p2_reaction_created),
                ("register_p2_im_message_reaction_deleted_v1", self._on_p2_reaction_deleted),
                ("register_p2_im_chat_member_bot_added_v1", self._on_p2_bot_added),
                ("register_p2_im_chat_member_bot_deleted_v1", self._on_p2_bot_deleted),
                ("register_p2_im_message_message_read_v1", self._on_p2_message_read),
        ):
            try:
                b = getattr(b, register)(handler)
            except Exception:  # pragma: no cover
                pass
        # drive.notice.comment_add_v1 has no typed processor in the
        # generated SDK. The wire payload may arrive under either schema:
        # the legacy callback channel uses p1 (event has ``uuid``), but
        # the modern WS frontier wraps the same event in a p2 envelope
        # (``schema=2.0``). Register the customized-event handler under
        # both so neither path logs "processor not found".
        b = b.register_p1_customized_event(
            "drive.notice.comment_add_v1", self._on_p1_comment_add
        )
        b = b.register_p2_customized_event(
            "drive.notice.comment_add_v1", self._on_p1_comment_add
        )
        return b.build()

    # ------------------------------------------------------------------
    # Raw sync entry points — schedule async work on the bg loop
    # ------------------------------------------------------------------
    def _on_p2_im_message_receive_v1(self, data: Any) -> None:
        self.schedule(self._handle_message_event(data))

    def _on_p2_card_action_trigger(
            self, data: P2CardActionTrigger
    ) -> P2CardActionTriggerResponse:
        try:
            if "cardAction" in self._handlers:
                self.schedule(self._handle_interaction_event(data))
        except Exception as e:
            logger.exception("cardAction schedule failed: %s", e)
        return P2CardActionTriggerResponse({})

    def _on_p2_reaction_created(self, data: Any) -> None:
        self.schedule(self._handle_reaction_event(data, action="create"))

    def _on_p2_reaction_deleted(self, data: Any) -> None:
        self.schedule(self._handle_reaction_event(data, action="delete"))

    def _on_p2_bot_added(self, data: Any) -> None:
        self.schedule(self._handle_bot_event(data, joined=True))

    def _on_p2_bot_deleted(self, data: Any) -> None:
        self.schedule(self._handle_bot_event(data, joined=False))

    def _on_p2_message_read(self, data: Any) -> None:
        self.schedule(self._handle_message_read_event(data))

    def _on_p1_comment_add(self, data: Any) -> None:
        self.schedule(self._handle_comment_event(data))

    # ------------------------------------------------------------------
    # Async event handlers
    # ------------------------------------------------------------------
    async def _handle_message_event(self, data: Any) -> None:
        try:
            event = getattr(data, "event", None)
            header = getattr(data, "header", None)
            event_id = getattr(header, "event_id", None)
            message = getattr(event, "message", None)
            sender = getattr(event, "sender", None)
            if message is None:
                return
            inbound = await self._pipeline.process(
                event_id=event_id,
                message_event=message,
                sender=sender,
            )
            if inbound is None:
                return
            if self._safety is not None:
                await self._safety.push_message(inbound)
            else:
                await self._dispatch_inbound_to_user(inbound)
        except Exception as e:
            logger.exception("FeishuChannel.handle_message_event failed: %s", e)

    async def _dispatch_inbound_to_user(self, inbound) -> None:
        await self._invoke("message", inbound)

    def _emit_reject(self, event: RejectEvent) -> None:
        handlers = self._handlers.get("reject")
        if not handlers:
            logger.debug(
                "policy reject message=%s reason=%s", event.message_id, event.reason
            )
            return
        for handler in list(handlers):
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    self.schedule(result)
            except Exception as e:  # pragma: no cover
                logger.warning("FeishuChannel.on('reject') raised: %s", e)

    async def _handle_interaction_event(self, data: P2CardActionTrigger) -> None:
        try:
            event = getattr(data, "event", None)
            action = getattr(event, "action", None)
            raw_value = getattr(action, "value", None)
            if isinstance(raw_value, str):
                try:
                    parsed = json.loads(raw_value)
                    raw_value = parsed if isinstance(parsed, dict) else {"value": parsed}
                except ValueError:
                    raw_value = {"value": raw_value}
            tag = getattr(action, "tag", None)
            context = getattr(event, "context", None)
            message_id = getattr(context, "open_message_id", None)
            chat_id = getattr(context, "open_chat_id", None)
            operator_open_id = getattr(
                getattr(event, "operator", None), "open_id", None
            )
            payload = CardActionEvent(
                message_id=message_id or "",
                chat_id=chat_id or "",
                operator=EventOperator(open_id=operator_open_id or ""),
                action=CardActionPayload(
                    tag=tag or "",
                    value=raw_value,
                    name=getattr(raw_value, "name", None)
                    if hasattr(raw_value, "name")
                    else None,
                ),
                raw=_coerce.obj_to_dict(data) or {},
            )
            # Route through safety.push_action (tier 2): dedup on a stable
            # action identity (tag + value payload) so Feishu's at-least-once
            # WS redelivery can't double-invoke the handler, and serialize by
            # chat_id so two fast clicks in the same chat are processed in
            # order. Node-SDK aligned.
            await self._through_action_safety(
                event_id=f"card:{payload.message_id}:{payload.operator.open_id}:"
                         f"{_card_action_identity(payload.action)}",
                queue_scope=payload.chat_id or payload.message_id or "",
                handler=lambda: self._invoke("cardAction", payload),
            )
        except Exception as e:
            logger.exception("FeishuChannel cardAction dispatch failed: %s", e)

    async def _through_action_safety(
            self,
            *,
            event_id: str,
            queue_scope: str,
            handler: Callable[[], Any],
    ) -> None:
        """Run ``handler`` through the safety tier-2 gate (dedup + lock +
        per-scope serial queue) when the pipeline exists; fall back to a
        direct invocation when it hasn't been built yet (early events during
        startup, unit tests that bypass ``connect``)."""
        safety = self._safety
        if safety is None:
            result = handler()
            if inspect.isawaitable(result):
                await result
            return

        async def _run() -> None:
            result = handler()
            if inspect.isawaitable(result):
                await result

        await safety.push_action(event_id, queue_scope or event_id, _run)

    async def _through_light_safety(
            self,
            *,
            event_id: str,
            handler: Callable[[], Any],
    ) -> None:
        """Tier-3 variant: dedup only (reaction add/remove). Same fallback
        semantics as :meth:`_through_action_safety`."""
        safety = self._safety
        if safety is None:
            result = handler()
            if inspect.isawaitable(result):
                await result
            return

        async def _run() -> None:
            result = handler()
            if inspect.isawaitable(result):
                await result

        await safety.push_light(event_id, _run)

    async def _handle_reaction_event(self, data: Any, *, action: str) -> None:
        cfg = self._config.inbound.reaction_notifications
        if cfg == "off":
            return
        try:
            event = getattr(data, "event", None) or {}
            user = getattr(event, "user_id", None)
            message_id = getattr(event, "message_id", None) or ""
            operator_open_id = (
                getattr(user, "open_id", None) if user is not None else None
            )
            emoji_type = getattr(
                getattr(event, "reaction_type", None), "emoji_type", None
            )
            action_time = getattr(event, "action_time", None)
            raw_dict = _coerce.obj_to_dict(data) or {}
            raw_event = raw_dict.get("event") if isinstance(raw_dict, dict) else {}
            if not isinstance(raw_event, dict):
                raw_event = {}
            chat_id = getattr(event, "chat_id", None) or raw_event.get("chat_id")
            chat_type = getattr(event, "chat_type", None) or raw_event.get("chat_type")
            context = self._sent_message_context.get(message_id)
            if context is not None:
                if not chat_id:
                    chat_id = context.chat_id
                if not chat_type:
                    chat_type = context.chat_type

            if cfg == "own":
                if message_id and message_id not in self._sent_messages:
                    return

            direction = "added" if action == "create" else "removed"
            payload = ReactionEvent(
                message_id=message_id,
                operator=EventOperator(open_id=operator_open_id or ""),
                emoji_type=emoji_type or "",
                action=direction,
                chat_id=chat_id or None,
                chat_type=chat_type or None,
                action_time=action_time,
                raw=raw_dict,
            )
            # Tier 3: dedup only. Reactions are idempotent state changes so
            # lock / serial queue would add latency for no benefit, but
            # WS redelivery would double-invoke without this guard.
            # Node-SDK aligned (pushLight).
            await self._through_light_safety(
                event_id=(
                    f"reaction:{message_id}:{operator_open_id or ''}:"
                    f"{emoji_type or ''}:{direction}"
                ),
                handler=lambda: self._invoke("reaction", payload),
            )
        except Exception as e:
            logger.exception("FeishuChannel reaction dispatch failed: %s", e)

    async def _handle_bot_event(self, data: Any, *, joined: bool) -> None:
        try:
            event = getattr(data, "event", None) or {}
            chat_id = getattr(event, "chat_id", None) or ""
            operator = getattr(event, "operator_id", None)
            open_id = getattr(operator, "open_id", None) if operator else None
            raw_dict = _coerce.obj_to_dict(data)
            payload_cls = BotAddedEvent if joined else BotLeaveEvent
            name = "botAdded" if joined else "botLeave"
            await self._invoke(
                name,
                payload_cls(
                    chat_id=chat_id,
                    operator=EventOperator(open_id=open_id or ""),
                    raw=raw_dict or {},
                ),
            )
        except Exception as e:
            logger.exception(
                "FeishuChannel bot-%s dispatch failed: %s",
                "added" if joined else "leave", e,
            )

    async def _handle_message_read_event(self, data: Any) -> None:
        try:
            event = getattr(data, "event", None) or {}
            reader = getattr(event, "reader", None)
            reader_open_id = getattr(reader, "reader_id", None) and getattr(
                reader.reader_id, "open_id", None
            )
            message_ids = list(getattr(event, "message_id_list", []) or [])
            await self._invoke(
                "messageRead",
                MessageReadEvent(
                    reader=EventOperator(open_id=reader_open_id or ""),
                    message_ids=message_ids,
                    raw=_coerce.obj_to_dict(data) or {},
                ),
            )
        except Exception as e:
            logger.exception("FeishuChannel messageRead dispatch failed: %s", e)

    async def _handle_comment_event(self, data: Any) -> None:
        try:
            # ``CustomizedEvent.event`` is the raw inner event payload as a
            # plain dict; the per-event timestamp lives on the envelope
            # (``header.create_time`` for p2, ``ts`` for p1) — not in the
            # inner dict — so pass it explicitly.
            raw_event = getattr(data, "event", None)
            header = getattr(data, "header", None)
            envelope_ts = (
                getattr(header, "create_time", None) if header is not None
                else getattr(data, "ts", None)
            )
            normalized = normalize_comment(
                raw_event if raw_event is not None else data,
                bot_open_id=self._bot_open_id,
                envelope_timestamp=envelope_ts,
            )
            if normalized is None:
                return
            # Tier 2: dedup + lock + per-file_token serial queue. Multiple
            # comments on the same document are ordered; redeliveries of the
            # same comment event are dropped. Node-SDK aligned.
            await self._through_action_safety(
                event_id=f"comment:{normalized.file_token}:{normalized.comment_id}",
                queue_scope=normalized.file_token,
                handler=lambda: self._invoke("comment", normalized),
            )
        except Exception as e:
            logger.exception("FeishuChannel comment dispatch failed: %s", e)

    def _notify_reconnecting(self) -> None:
        for h in list(self._handlers.get("reconnecting", [])):
            try:
                h()
            except Exception as e:  # pragma: no cover
                logger.warning("reconnecting handler raised: %s", e)

    def _notify_reconnected(self) -> None:
        for h in list(self._handlers.get("reconnected", [])):
            try:
                h()
            except Exception as e:  # pragma: no cover
                logger.warning("reconnected handler raised: %s", e)

    # ------------------------------------------------------------------
    # Outbound: send / stream / message ops (node-aligned)
    # ------------------------------------------------------------------
    async def upload_media(
            self,
            source: MediaSource,
            *,
            kind: Literal["image", "file"],
            file_name: Optional[str] = None,
            file_type: Optional[str] = None,
    ) -> str:
        """Upload a media resource and return its Feishu ``image_key`` /
        ``file_key`` without sending a message.

        Public wrapper over the internal :func:`resolve_media_key` helper —
        intended for callers that need to construct custom post AST (e.g.
        ``audio + caption`` / ``file + caption``, which Feishu does not render
        natively but accepts as ``msg_type=post`` with ``tag:audio|file``
        nodes), or want to pre-upload + cache a key for cross-chat reuse.

        ``source`` must be a :class:`MediaSource`; pass an explicit kind:

        - ``MediaSource(kind="buffer", buffer=...)`` — in-memory bytes
        - ``MediaSource(kind="file", path=...)`` — local file
        - ``MediaSource(kind="url", url=...)`` — remote URL (SSRF-checked
          against ``OutboundConfig.ssrf_allowlist``)
        - ``MediaSource(kind="key", key=...)`` — pre-uploaded key (returned
          unchanged; no upload performed)

        ``kind`` selects the upload route: ``"image"`` → image upload (returns
        ``image_key``), ``"file"`` → file upload (returns ``file_key``). For
        audio / video, use ``kind="file"`` with ``file_type="opus"`` /
        ``"mp4"`` — Feishu treats them as typed file uploads at the wire
        level. ``file_name`` is shown in Feishu UI for ``kind="file"``.

        Failures raise :class:`FeishuChannelError`:

        - ``UPLOAD_FAILED`` — server rejection, network error, missing local
          file, malformed response, or empty ``MediaSource(kind="key", key="")``
        - ``SSRF_BLOCKED`` — URL source without an allowlist match

        SSRF allowlist is taken from ``self.config.outbound.ssrf_allowlist``
        — callers do **not** mutate the source object.
        """
        if not isinstance(source, MediaSource):
            raise TypeError(
                f"upload_media: source must be a MediaSource; "
                f"got {type(source).__name__}"
            )
        if kind not in ("image", "file"):
            raise ValueError(
                f"upload_media: kind must be 'image' or 'file'; got {kind!r}"
            )

        from .outbound.media.uploader import resolve_media_key

        key = await resolve_media_key(
            self._sender._driver,
            source,
            kind,
            file_name=file_name,
            file_type=file_type,
            ssrf_allowlist=self._config.outbound.ssrf_allowlist,
        )
        if key is None:
            # ``resolve_media_key`` returns None only for "nothing to upload"
            # inputs (kind="key" with empty key, or unhandled source shape).
            # The public method commits to ``str`` — convert to UPLOAD_FAILED
            # so callers don't need to handle Optional.
            raise FeishuChannelError(
                FeishuChannelErrorCode.UPLOAD_FAILED,
                f"upload_media: source has no uploadable content "
                f"(source.kind={source.kind!r})",
                context={"source_kind": source.kind},
            )
        return key

    async def send(self, to, message, opts=None) -> SendResult:
        """Send a message to a chat / user / email.

        ``message`` may be a dict (``{"text": "..."}``, ``{"markdown": "..."}``,
        ``{"image": {...}}``, …), a typed :class:`OutboundMessage` dataclass,
        or a bare string (shorthand for markdown). See :mod:`._coerce` for the
        full accepted shape.

        Errors: both raised exceptions (coercion errors, transport failures)
        AND ``SendResult.fail(...)`` outcomes are also forwarded to any
        handler registered via ``channel.on("error", ...)``, so apps can
        centralise failure observation. The error is still returned /
        raised to the immediate caller as well — forwarding does not swallow.
        """
        try:
            outbound = _coerce.coerce_outbound(message)
            send_opts = _coerce.coerce_send_opts(opts)
            rit = send_opts.receive_id_type or infer_receive_id_type(to)
            result = await self._sender.send(
                outbound,
                receive_id=to,
                receive_id_type=rit,
                reply_to=send_opts.reply_to,
                reply_in_thread=send_opts.reply_in_thread,
                reply_target_gone=send_opts.reply_target_gone,
                uuid_=send_opts.uuid,
            )
        except Exception as e:
            await self._forward_outbound_error(e)
            raise
        if not result.success and result.error is not None:
            await self._forward_outbound_error(result.error)
        if result.success:
            self._remember_sent_message_context(
                result,
                chat_id=to if rit == "chat_id" and isinstance(to, str) else None,
                receive_id_type=rit,
            )
        return result

    async def _forward_outbound_error(self, err: Any) -> None:
        """Fan-out a send/stream failure to any ``on("error", ...)`` handlers.

        :class:`SendError` is a dataclass without ``__traceback__`` or a
        ``str``-friendly form, so generic diagnostic plumbing
        (``logger.exception``, Sentry) chokes on it. Wrap it in
        :class:`OutboundSendError` before dispatching. The wrapping does not
        affect the value returned by ``channel.send()`` (still
        :class:`SendResult`).

        Never swallows — the error still propagates to the direct caller.
        Handler exceptions are logged but otherwise ignored.
        """
        if isinstance(err, SendError):
            err = OutboundSendError(err)
        for h in list(self._handlers.get("error", [])):
            try:
                result = h(err)
                if inspect.isawaitable(result):
                    await result
            except Exception as inner:  # pragma: no cover - defensive
                logger.warning("on('error') handler raised: %s", inner)

    async def stream(self, to, spec: Dict[str, Any], opts=None) -> SendResult:
        """Stream a message progressively.

        ``spec`` is either ``{"markdown": producer}`` or
        ``{"card": {"initial": ..., "producer": ...}}``.

        Errors (coercion + stream controller raises) are also forwarded to
        any ``on("error", ...)`` handlers before being re-raised to the
        caller, same contract as :meth:`send`.
        """
        try:
            if not isinstance(spec, dict):
                raise TypeError("stream spec must be a dict")
            send_opts = _coerce.coerce_send_opts(opts)
            rit = send_opts.receive_id_type or infer_receive_id_type(to)
        except Exception as e:
            await self._forward_outbound_error(e)
            raise

        if "markdown" in spec:
            # Markdown streaming uses the CardKit preallocation flow — every
            # throttle tick is an `update_card_element_content` call (seq-ordered
            # element patch) instead of a full-card PATCH. See
            # :mod:`.outbound.streaming.markdown_stream` for the node-aligned
            # protocol.
            ctl = MarkdownStreamController(
                to=to,
                receive_id_type=rit,
                reply_to=send_opts.reply_to,
                reply_in_thread=send_opts.reply_in_thread,
                reply_target_gone=send_opts.reply_target_gone,
                create_card_instance=self.create_card_instance,
                send_card_by_reference=self.send_card_by_reference,
                update_card_element_content=self.update_card_element_content,
                finish_streaming_card=self.finish_streaming_card,
            )
            try:
                mid = await ctl.run(spec["markdown"])
            except Exception as e:
                await self._forward_outbound_error(e)
                raise
            return SendResult.ok(message_id=mid)

        if "card" in spec:
            card_def = spec["card"]
            initial = card_def.get("initial") if isinstance(card_def, dict) else None
            producer = card_def.get("producer") if isinstance(card_def, dict) else None
            if initial is None or not callable(producer):
                err = TypeError("card stream requires {initial, producer}")
                await self._forward_outbound_error(err)
                raise err
            ctl = CardStreamController(
                initial=initial,
                ensure_created=lambda snap: self._ensure_card_snapshot(
                    to, rit, snapshot=snap,
                    reply_to=send_opts.reply_to,
                    reply_in_thread=send_opts.reply_in_thread,
                    reply_target_gone=send_opts.reply_target_gone,
                ),
                patch_card=self._patch_card,
            )
            try:
                mid = await ctl.run(producer)
            except Exception as e:
                await self._forward_outbound_error(e)
                raise
            return SendResult.ok(message_id=mid)

        err = TypeError("stream spec must contain 'markdown' or 'card'")
        await self._forward_outbound_error(err)
        raise err

    async def update_card(self, message_id: str, card: Dict[str, Any]) -> SendResult:
        """Update a card message (node-aligned). Returns a :class:`SendResult`."""
        raw = await self._patch_card(message_id, card)
        return _coerce.result_from_raw(raw, message_id=message_id)

    async def recall_message(self, message_id: str) -> SendResult:
        raw = await self._driver.delete_message(message_id=message_id)
        return _coerce.result_from_raw(raw, message_id=message_id)

    async def add_reaction(self, message_id: str, emoji_type: str) -> SendResult:
        raw = await self._driver.add_reaction(
            message_id=message_id, emoji_type=emoji_type
        )
        return _coerce.result_from_raw(raw, message_id=message_id)

    async def remove_reaction(self, message_id: str, reaction_id: str) -> SendResult:
        raw = await self._driver.remove_reaction(
            message_id=message_id, reaction_id=reaction_id
        )
        return _coerce.result_from_raw(raw, message_id=message_id)

    async def edit_message(self, message_id: str, message) -> SendResult:
        """Edit a previously sent text or post message.

        Accepted message shapes mirror send() for editable types: str,
        {"markdown": ...}, {"text": ...}, {"post": ...}, OutboundText,
        and OutboundPost. Cards must use update_card(); media/share/sticker
        messages are not editable through this method.
        """
        outbound = _coerce.coerce_outbound(message)
        if isinstance(outbound, OutboundCard):
            raise TypeError("edit_message does not support cards; use update_card()")
        if not isinstance(outbound, (OutboundText, OutboundPost)):
            raise TypeError(
                "edit_message only supports text/post messages; "
                f"got {type(outbound).__name__}"
            )
        body = await self._sender.materialize_for_edit(outbound)
        raw = await self._driver.update_message(
            message_id=message_id,
            msg_type=body["msg_type"],
            content=body["content"],
        )
        return _coerce.result_from_raw(raw, message_id=message_id)

    async def download_resource(
            self,
            file_key: str,
            resource_type: str = "image",
            message_id: Optional[str] = None,
    ) -> Optional[bytes]:
        return await self._download_media(
            message_id=message_id or "",
            file_key=file_key,
            resource_type=resource_type,
        )

    async def _download_media(
            self, *, message_id: str, file_key: str, resource_type: str
    ) -> Optional[bytes]:
        return await _api_helpers.download_media(
            self._client,
            message_id=message_id,
            file_key=file_key,
            resource_type=resource_type,
        )

    async def download_resource_to_file(
            self,
            file_key: str,
            *,
            resource_type: str = "image",
            message_id: Optional[str] = None,
            dest_dir: "Path",
            file_name: Optional[str] = None,
    ) -> "Path":
        """Download a resource to disk and return the absolute path.

        Args:
            file_key: opaque resource identifier from the inbound event.
            resource_type: ``image`` / ``file`` / ``audio`` / ``video``.
            message_id: when supplied, downloads via the message-resource
                endpoint; without it, falls back to the standalone
                image/file endpoints.
            dest_dir: target directory (auto-created if missing).
            file_name: override the auto-generated filename. When None, the
                file is named ``<file_key><suffix>`` where ``<suffix>`` is
                inferred from the response's content-type / file_name.

        Returns:
            Absolute path to the downloaded file.

        Raises:
            FeishuChannelError(DOWNLOAD_FAILED): when the download fails or
                the response has no body.
        """
        from pathlib import Path
        import os
        import tempfile

        body, meta = await _api_helpers.download_media_with_meta(
            self._client,
            message_id=message_id or "",
            file_key=file_key,
            resource_type=resource_type,
        )
        if body is None:
            raise FeishuChannelError(
                FeishuChannelErrorCode.DOWNLOAD_FAILED,
                f"download failed: file_key={file_key} resource_type={resource_type}",
            )

        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        if file_name:
            name = file_name
        else:
            suffix = self._infer_suffix(meta, resource_type)
            name = f"{file_key}{suffix}"
        name = self._safe_download_file_name(name)
        out = dest_dir / name

        # Atomic: write to tmp file in same dir, then rename.
        fd, tmp_path = tempfile.mkstemp(prefix=".dl-", dir=str(dest_dir))
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(body)
            os.replace(tmp_path, out)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return out

    @staticmethod
    def _safe_download_file_name(name: str) -> str:
        """Validate a download filename before joining it under dest_dir."""
        from pathlib import PureWindowsPath
        import os

        name = (name or "").replace("\x00", "")
        win = PureWindowsPath(name)
        if (
                not name
                or name in (".", "..")
                or os.path.isabs(name)
                or "/" in name
                or "\\" in name
                or win.drive
                or win.root
                or any(part in ("", ".", "..") for part in win.parts)
        ):
            raise FeishuChannelError(
                FeishuChannelErrorCode.DOWNLOAD_FAILED,
                f"unsafe download file name: {name!r}",
            )
        return name

    @staticmethod
    def _infer_suffix(meta: Optional[str], resource_type: str) -> str:
        """Best-effort suffix derivation from content-type / filename.

        Falls back to ``.bin`` when nothing is parseable, then to type-default
        suffixes for the four common ``resource_type`` values.
        """
        import mimetypes

        if meta:
            # If meta looks like a filename (has a dot in last segment),
            # return its suffix directly.
            if "/" not in meta and "." in meta:
                ext = "." + meta.rsplit(".", 1)[-1]
                if 1 < len(ext) <= 6:
                    return ext.lower()
            # Otherwise treat as a MIME type
            ext = mimetypes.guess_extension(meta.split(";", 1)[0].strip())
            if ext:
                return ext

        return {
            "image": ".jpg",
            "audio": ".mp3",
            "video": ".mp4",
            "file": ".bin",
        }.get(resource_type, ".bin")

    async def get_chat_info(self, chat_id: str) -> Optional[ChatInfo]:
        """Fetch chat metadata. Returns None on API failure."""
        return await _api_helpers.fetch_chat_info(self._client, chat_id)

    # ------------------------------------------------------------------
    # CardKit preallocation API (node-aligned)
    # ------------------------------------------------------------------
    async def create_card_instance(self, spec: Dict[str, Any]) -> str:
        """Create a pre-allocated card via ``POST /open-apis/cardkit/v1/card``.

        Returns the ``card_id`` string. Use with :meth:`send_card_by_reference`
        / :meth:`update_card_element_content` / :meth:`finish_streaming_card`
        for the CardKit typewriter-streaming flow.
        """
        raw = await self._driver.cardkit_create(
            body={"type": "card_json", "data": json.dumps(spec, ensure_ascii=False)}
        )
        if not isinstance(raw, dict) or raw.get("code", 0) != 0:
            raise FeishuChannelError(
                FeishuChannelErrorCode.UNKNOWN,
                f"create_card_instance failed: {raw}",
            )
        data = raw.get("data") or {}
        card_id = data.get("card_id")
        if not card_id:
            raise FeishuChannelError(
                FeishuChannelErrorCode.UNKNOWN,
                f"create_card_instance response missing card_id: {raw}",
            )
        return str(card_id)

    async def send_card_by_reference(
            self,
            to: str,
            card_id: str,
            *,
            receive_id_type: Optional[str] = None,
            reply_to: Optional[str] = None,
            reply_in_thread: Optional[bool] = None,
            reply_target_gone: str = "fresh",
    ) -> SendResult:
        """Send a message that references a pre-allocated card (see
        :meth:`create_card_instance`)."""
        rit = receive_id_type or infer_receive_id_type(to)
        return await self._sender.send(
            OutboundCard(card={"type": "card", "data": {"card_id": card_id}}),
            receive_id=to,
            receive_id_type=rit,
            reply_to=reply_to,
            reply_in_thread=reply_in_thread,
            reply_target_gone=reply_target_gone,
        )

    async def update_card_element_content(
            self,
            card_id: str,
            element_id: str,
            content: str,
            sequence: int,
    ) -> None:
        """Typewriter-update a card element. ``sequence`` must strictly increase."""
        raw = await self._driver.cardkit_update_element(
            card_id=card_id,
            element_id=element_id,
            body={"content": content, "sequence": sequence},
        )
        if isinstance(raw, dict) and raw.get("code", 0) != 0:
            raise FeishuChannelError(
                FeishuChannelErrorCode.UNKNOWN,
                f"update_card_element_content failed: {raw}",
            )

    async def finish_streaming_card(self, card_id: str, sequence: int) -> None:
        """Close ``streaming_mode`` on a pre-allocated card."""
        settings = json.dumps(
            {"config": {"streaming_mode": False}}, ensure_ascii=False
        )
        raw = await self._driver.cardkit_update_settings(
            card_id=card_id,
            body={"settings": settings, "sequence": sequence},
        )
        if isinstance(raw, dict) and raw.get("code", 0) != 0:
            raise FeishuChannelError(
                FeishuChannelErrorCode.UNKNOWN,
                f"finish_streaming_card failed: {raw}",
            )

    # ------------------------------------------------------------------
    # Card streaming internals
    # ------------------------------------------------------------------
    async def _ensure_card(
            self,
            to,
            rit,
            *,
            initial_text,
            reply_to,
            reply_in_thread,
            reply_target_gone="fresh",
    ) -> str:
        """Compatibility wrapper for older internal card-stream call sites."""
        return await self._ensure_card_snapshot(
            to, rit,
            snapshot={
                "schema": "2.0",
                "config": {"streaming_mode": True, "summary": {"content": ""}},
                "body": {"elements": [{"tag": "markdown", "content": initial_text or "..."}]},
            },
            reply_to=reply_to,
            reply_in_thread=reply_in_thread,
            reply_target_gone=reply_target_gone,
        )

    async def _ensure_card_snapshot(
            self,
            to,
            rit,
            *,
            snapshot,
            reply_to,
            reply_in_thread,
            reply_target_gone="fresh",
    ) -> str:
        result = await self._sender.send(
            OutboundCard(card=snapshot),
            receive_id=to,
            receive_id_type=rit,
            reply_to=reply_to,
            reply_in_thread=reply_in_thread,
            reply_target_gone=reply_target_gone,
        )
        if not result.success or not result.message_id:
            code = result.error.code if result.error else FeishuChannelErrorCode.UNKNOWN
            raise FeishuChannelError(
                code, f"failed to create streaming card: {result.error}"
            )
        return result.message_id

    async def _patch_card(self, message_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        raw = await self._driver.patch_message(
            message_id=message_id,
            content=json.dumps(card, ensure_ascii=False),
        )
        code = (raw or {}).get("code", 0)
        if code != 0:
            logger.warning(
                "channel.card_patch: patch failed code=%s msg=%s",
                code, (raw or {}).get("msg"),
            )
        return raw

    # ------------------------------------------------------------------
    # Fetch payload
    # ------------------------------------------------------------------
    async def fetch_message(self, message_id: str) -> Dict[str, Any]:
        """Fetch a message by ID and return the raw Feishu ``im.v1.message.get``
        response as a dict.

        This is a thin wrapper over the underlying OpenAPI call — no
        normalization is performed. Use it for cases like "look up the text
        of a message the user replied to" where you need ad-hoc access to
        the wire payload. For the typed :class:`InboundMessage` shape, feed
        events through the inbound pipeline normally.
        """
        return await self._driver.fetch_message(message_id)

    # Alias used by the internal pipeline (kept stable for dependency
    # injection; external callers should prefer ``fetch_message``).
    async def _fetch_message_payload(self, message_id: str) -> Dict[str, Any]:
        return await self._driver.fetch_message(message_id)

    # ------------------------------------------------------------------
    # UAT (user access token) — exposed for callers that need it explicitly
    # ------------------------------------------------------------------
    async def require_user_auth(
            self,
            user_open_id: str,
            scopes: list,
            *,
            prompt_context: Any = None,
    ) -> UAT:
        """Resolve a user access token for ``user_open_id``, running the
        device flow if needed. ``prompt_context`` must expose
        ``respond(card)`` if the user needs a prompt card (usually the
        original interaction carrier)."""
        return await require_user_auth(
            device_flow=self._device_flow,
            token_store=self._token_store,
            uat_config=self._config.uat,
            user_open_id=user_open_id,
            scopes=scopes,
            context=prompt_context,
        )

    def _track_sent_message(self, message_id: str) -> None:
        if not message_id:
            return
        self._sent_messages[message_id] = time.time()
        self._sent_messages.move_to_end(message_id)
        while len(self._sent_messages) > self._sent_messages_max:
            evicted, _ = self._sent_messages.popitem(last=False)
            self._sent_message_context.pop(evicted, None)

    def _remember_sent_message_context(
            self,
            result: SendResult,
            *,
            chat_id: Optional[str],
            receive_id_type: Optional[str],
    ) -> None:
        message_ids = list(result.chunk_ids or [])
        if result.message_id and result.message_id not in message_ids:
            message_ids.insert(0, result.message_id)
        for message_id in message_ids:
            self._track_sent_message(message_id)
            if not chat_id:
                self._sent_message_context.pop(message_id, None)
                continue
            self._sent_message_context[message_id] = _SentMessageContext(
                message_id=message_id,
                chat_id=chat_id,
                receive_id_type=receive_id_type,
            )
            self._sent_message_context.move_to_end(message_id)
