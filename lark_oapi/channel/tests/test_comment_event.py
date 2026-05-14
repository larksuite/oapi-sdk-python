"""Tests for normalize_comment and dispatcher wiring.

Two regressions are guarded here:

1. The channel registers ``drive.notice.comment_add_v1`` under both ``p1`` and
   ``p2`` schemas. The WS frontier wraps in a p2 envelope; legacy callbacks
   use p1.

2. After registration, the live comment payload still surfaced operator
   open_id / mentioned_bot / timestamp as null — the original
   ``normalize_comment`` was guessing at field names that don't exist in
   the wire format. Real shape (observed end-to-end against a Feishu
   tenant 2026-04-27): operator at ``notice_meta.from_user_id``,
   mentioned-bot is the boolean ``is_mentioned``, timestamp is
   ``create_time`` as a millisecond string.
"""

import threading

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.normalize.comment import CommentEvent, normalize_comment


# ---------------------------------------------------------------------------
# normalize_comment — real wire format
# ---------------------------------------------------------------------------


def test_full_payload_real_wire_format():
    """Mirror a realistic ``drive.notice.comment_add_v1`` WS payload."""
    payload = {
        "event": {
            "file_token": "doc_token_x",
            "file_type": "docx",
            "comment_id": "cmt_1",
            "reply_id": "rpl_1",
            "is_mentioned": True,
            "create_time": "1700000000000",
            "notice_meta": {
                "from_user_id": {
                    "open_id": "ou_op",
                    "user_id": "u_op",
                    "union_id": "on_op",
                },
                "to_user_id": {"open_id": "ou_bot"},
                "file_token": "doc_token_x",
                "file_type": "docx",
                "is_mentioned": True,
                "timestamp": "1700000000000",
                "notice_type": "comment_add",
            },
        }
    }
    c = normalize_comment(payload)
    assert isinstance(c, CommentEvent)
    assert c.file_token == "doc_token_x"
    assert c.file_type == "docx"
    assert c.comment_id == "cmt_1"
    assert c.reply_id == "rpl_1"
    assert c.operator.open_id == "ou_op"
    assert c.operator.user_id == "u_op"
    assert c.operator.union_id == "on_op"
    assert c.mentioned_bot is True
    assert c.timestamp == 1700000000000


def test_missing_file_token_returns_none():
    payload = {"event": {"comment_id": "x"}}
    assert normalize_comment(payload) is None


def test_missing_operator_returns_none():
    """Half-populated payloads (no operator) are dropped instead of
    delivered with operator.open_id == None."""
    payload = {
        "event": {
            "file_token": "t",
            "file_type": "docx",
            "comment_id": "c",
            "create_time": "1",
            # notice_meta missing → no operator → drop
        }
    }
    assert normalize_comment(payload) is None


def test_envelope_timestamp_used_when_inner_event_omits_it():
    """The real WS payload puts ``create_time`` on the p2 envelope's
    ``header``, not the inner event dict. Without this fallback, every
    delivered ``CommentEvent`` would have ``timestamp=0``."""
    payload = {
        "event": {
            "file_token": "doc_token_x",
            "file_type": "docx",
            "comment_id": "cmt_no_inner_ts",
            "is_mentioned": True,
            "notice_meta": {"from_user_id": {"open_id": "ou_op"}},
            # NB: no create_time / action_time / timestamp anywhere inside
        }
    }
    c = normalize_comment(payload, envelope_timestamp="1700000000000")
    assert c is not None
    assert c.timestamp == 1700000000000


def test_legacy_top_level_user_id_fallback():
    """Older p1 callbacks ship the operator at top level as ``user_id``
    instead of ``notice_meta.from_user_id``. Don't break those."""
    payload = {
        "event": {
            "file_token": "t1",
            "file_type": "sheet",
            "comment_id": "cmt_abc",
            "user_id": {"open_id": "ou_legacy", "union_id": "on_legacy"},
            "is_mention": True,
            "action_time": "1650000000000",
        }
    }
    c = normalize_comment(payload)
    assert c is not None
    assert c.operator.open_id == "ou_legacy"
    assert c.operator.union_id == "on_legacy"
    assert c.mentioned_bot is True
    assert c.timestamp == 1650000000000


def test_is_mentioned_false_propagates():
    """When the bot was NOT @-mentioned (e.g. an at-document comment), the
    flag must surface as False. The result must not depend on a mentions array
    that doesn't exist on the wire."""
    payload = {
        "event": {
            "file_token": "t",
            "file_type": "docx",
            "comment_id": "c",
            "is_mentioned": False,
            "create_time": "1",
            "notice_meta": {"from_user_id": {"open_id": "ou_op"}},
        }
    }
    c = normalize_comment(payload)
    assert c is not None and c.mentioned_bot is False


# ---------------------------------------------------------------------------
# Dispatcher wiring — both p1 and p2 must be registered
# ---------------------------------------------------------------------------


def _client() -> FeishuChannel:
    return FeishuChannel(app_id="cli_test", app_secret="secret_test")


def test_dispatcher_registers_both_schemas_for_comment_add():
    c = _client()
    c._ensure_bg_loop()
    dispatcher = c._build_dispatcher()
    keys = set(dispatcher._processorMap.keys())
    # WS frontier wraps even legacy events in a p2 envelope; the legacy
    # HTTP callback uses p1. Without both, half the deployments log
    # ``processor not found``.
    assert "p1.drive.notice.comment_add_v1" in keys, (
        f"missing p1 processor; got {sorted(keys)}"
    )
    assert "p2.drive.notice.comment_add_v1" in keys, (
        f"missing p2 processor; got {sorted(keys)}"
    )


def test_incoming_comment_event_invokes_comment_handler():
    """End-to-end: feed a CustomizedEvent (real wire format) into the
    dispatcher processor and assert ``on("comment", ...)`` fires with a
    fully-populated ``CommentEvent``."""
    from lark_oapi.event.custom import CustomizedEvent

    c = _client()
    c._ensure_bg_loop()
    dispatcher = c._build_dispatcher()

    got: list[CommentEvent] = []
    done = threading.Event()

    def _on_comment(ev: CommentEvent) -> None:
        got.append(ev)
        done.set()

    c.on("comment", _on_comment)

    ctx = CustomizedEvent()
    ctx.event = {
        "file_token": "doc_token_case",
        "file_type": "docx",
        "comment_id": "cmt_42",
        "reply_id": "rpl_42",
        "is_mentioned": True,
        "create_time": "1712000000000",
        "notice_meta": {
            "from_user_id": {
                "open_id": "ou_op_user",
                "user_id": "u_op",
            },
            "is_mentioned": True,
            "timestamp": "1712000000000",
        },
    }

    # Use the p2 processor (modern WS path) — the regression chain.
    processor = dispatcher._processorMap["p2.drive.notice.comment_add_v1"]
    processor.do(ctx)
    assert done.wait(timeout=2.0), "comment handler was not invoked within 2s"
    assert len(got) == 1
    ev = got[0]
    assert ev.file_token == "doc_token_case"
    assert ev.comment_id == "cmt_42"
    assert ev.operator.open_id == "ou_op_user"
    assert ev.operator.user_id == "u_op"
    assert ev.mentioned_bot is True
    assert ev.timestamp == 1712000000000
