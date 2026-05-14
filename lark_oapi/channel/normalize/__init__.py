"""Normalize: raw Lark events → structured InboundMessage / *Event shapes.

Houses the inbound pipeline, message-content registry, dedup store, mention
parser (node-aligned ``extract_mentions`` / ``resolve_mentions``), and the
flat-text/resource flattener.
"""

from .comment import CommentEvent, CommentOperator, normalize_comment
from .dedup import DedupStore, InMemoryDedupStore, make_event_key, make_message_key
from .flatten import flatten
from .mentions import (
    MentionExtraction,
    extract_mentions,
    is_mention_all,
    parse_at_tags,
    resolve_mentions,
)
from .pipeline import InboundPipeline
from .registry import parse_message_content

__all__ = [
    "CommentEvent",
    "CommentOperator",
    "DedupStore",
    "InMemoryDedupStore",
    "InboundPipeline",
    "MentionExtraction",
    "extract_mentions",
    "flatten",
    "is_mention_all",
    "make_event_key",
    "make_message_key",
    "normalize_comment",
    "parse_at_tags",
    "parse_message_content",
    "resolve_mentions",
]
