"""Safety pipeline — dedup, stale detection, policy, lock, batch+queue."""

from .chat_pipeline import ChatPipeline, ChatPipelineManager, merge_batch
from .pipeline import SafetyPipeline
from .policy_gate import PolicyDecision, PolicyGate
from .processing_lock import ProcessingLock
from .dedup_cache import SeenCache
from .stale_detector import DEFAULT_STALE_MS, is_stale
from .types import (
    BatchConfig,
    ChatQueueConfig,
    DedupConfig,
    MediaBatchConfig,
    RejectEvent,
    RejectReason,
    TextBatchConfig,
)

__all__ = [
    "BatchConfig",
    "ChatPipeline",
    "ChatPipelineManager",
    "ChatQueueConfig",
    "DEFAULT_STALE_MS",
    "DedupConfig",
    "MediaBatchConfig",
    "PolicyDecision",
    "PolicyGate",
    "ProcessingLock",
    "RejectEvent",
    "RejectReason",
    "SafetyPipeline",
    "SeenCache",
    "TextBatchConfig",
    "is_stale",
    "merge_batch",
]
