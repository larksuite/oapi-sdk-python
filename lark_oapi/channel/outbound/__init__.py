"""Outbound pipeline: convert OutboundMessage → Lark API calls.

Sub-packages:
    markdown/ — markdown → post-AST + code-fence-aware splitter
    media/    — SSRF guard + zero-dep duration parsers + uploader
    streaming/— streaming controllers + queue/throttle primitives
"""

from .markdown import markdown_to_post_ast, split_with_code_fences
from .media import assert_public_url, parse_mp4_duration, parse_opus_duration
from .retry import with_retry
from .routing import infer_receive_id_type
from .sender import OutboundSender, chunk_text

__all__ = [
    "OutboundSender",
    "assert_public_url",
    "chunk_text",
    "infer_receive_id_type",
    "markdown_to_post_ast",
    "parse_mp4_duration",
    "parse_opus_duration",
    "split_with_code_fences",
    "with_retry",
]
