"""Safety-layer primitive types.

``DedupConfig``, ``TextBatchConfig``, and ``ChatQueueConfig`` used to live
here but were promoted into :mod:`..config` so the public schema is
self-contained and to break a circular import (safety eagerly imports
``SafetyPipeline`` which needs :class:`PolicyConfig`). They are re-exported
from this module as back-compat aliases.

``MediaBatchConfig`` lives here and is consumed by
:class:`MediaPipelineManager` (wired into :class:`SafetyPipeline` so
compatible-kind media within ``delay_ms`` are merged into a single dispatch
carrying ``InboundMessage.batched_sources``). Default is ``enabled=False``
so existing deployments see no behaviour change. ``BatchConfig`` is kept as
a legacy compound shape for back-compat and is not consumed by the pipeline.
"""

from dataclasses import dataclass, field
from typing import Literal

# Re-export from the public schema so existing `from .types import …` call
# sites inside the safety package keep working.
from ..config import ChatQueueConfig, DedupConfig, TextBatchConfig  # noqa: F401

__all__ = [
    "BatchConfig",
    "ChatQueueConfig",
    "DedupConfig",
    "MediaBatchConfig",
    "RejectEvent",
    "RejectReason",
    "TextBatchConfig",
]

# ---- Reject taxonomy --------------------------------------------------------

RejectReason = Literal[
    # Non-policy reasons
    "stale",
    "duplicate",
    "lock_contention",
    "self_sent",
        # Policy reasons (unified policy_ prefix)
    "policy_dm_disabled",
    "policy_group_disabled",
    "policy_dm_not_in_allowlist",
    "policy_group_not_in_allowlist",
    "policy_blocklist",
    "policy_admin_only",
    "policy_no_mention",
    "policy_mention_all_blocked",
    "policy_sender_not_allowed",
]


@dataclass
class RejectEvent:
    """Emitted by SafetyPipeline when a message is filtered out.

    Carries just enough info for the caller to log or surface the decision.
    Reasons include both policy decisions and runtime safety gates such as
    stale messages, duplicate delivery, lock contention, and self-sent drops.
    """

    message_id: str
    chat_id: str
    sender_id: str
    reason: RejectReason


# ---- Batch config ----------------------------------------------------------


@dataclass
class MediaBatchConfig:
    """Debounce + bundle successive media messages in the same chat.

    A run of compatible media messages (same kind, same chat, no intervening
    text) within ``delay_ms`` is collapsed into a single dispatch carrying
    :attr:`InboundMessage.batched_sources` — the list of source messages in
    arrival order.

    Default: ``enabled=False`` so existing deployments see no behavior change.
    Opt in by setting ``enabled=True``.
    """

    enabled: bool = False
    delay_ms: int = 800
    max_items: int = 9
    compatible_kinds: frozenset = field(
        default_factory=lambda: frozenset({"image", "file", "audio", "video"})
    )


@dataclass
class BatchConfig:
    """Reserved: text + media batch settings as a pair (legacy shape, kept
    for back-compat — new code should use TextBatchConfig + MediaBatchConfig
    directly via SafetyConfig)."""

    text: TextBatchConfig = field(default_factory=TextBatchConfig)
    media: MediaBatchConfig = field(default_factory=MediaBatchConfig)
