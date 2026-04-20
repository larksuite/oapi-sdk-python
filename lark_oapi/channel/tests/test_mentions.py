"""Tests for mention parsing — node-aligned extract + resolve API."""

from lark_oapi.channel.normalize.mentions import (
    extract_mentions,
    is_mention_all,
    parse_at_tags,
    resolve_mentions,
    text_has_mention_all,
)


def test_extract_then_resolve_placeholders():
    text = "hi @_user_1 and @_user_2"
    events = [
        {"key": "@_user_1", "id": {"open_id": "ou_A"}, "name": "Alice"},
        {"key": "@_user_2", "id": {"open_id": "ou_B"}, "name": "Bob"},
    ]
    ext = extract_mentions(events)
    assert ext.mentioned_all is False
    assert len(ext.mention_list) == 2
    assert ext.mention_list[0].open_id == "ou_A"
    assert ext.mentions_by_open_id["ou_A"].name == "Alice"

    out = resolve_mentions(text, ext)
    assert out == "hi @Alice and @Bob"


def test_mention_all_detected_and_excluded():
    events = [{"key": "@_all", "id": {"user_id": "all"}, "name": "所有人"}]
    ext = extract_mentions(events)
    assert ext.mentioned_all is True
    assert ext.mention_list == []
    # Unresolved placeholder stays as-is.
    assert resolve_mentions("@_user_1 hi", ext) == "@_user_1 hi"


def test_is_mention_all_detection():
    assert is_mention_all({"key": "@_all"})
    assert is_mention_all({"id": {"user_id": "all"}})
    assert not is_mention_all({"key": "@_user_1", "id": {"user_id": "u1"}})


def test_unresolved_placeholder_kept_untouched():
    ext = extract_mentions([])
    assert resolve_mentions("hi @_user_9", ext) == "hi @_user_9"


def test_strip_bot_mentions_removes_bot_placeholder():
    events = [
        {"key": "@_user_1", "id": {"open_id": "ou_bot"}, "name": "Bot"},
        {"key": "@_user_2", "id": {"open_id": "ou_A"}, "name": "Alice"},
    ]
    ext = extract_mentions(events, bot_open_id="ou_bot")
    assert ext.mentioned_bot is True
    # Bot excluded from mention_list but kept in `mentions` for strip.
    assert [m.open_id for m in ext.mention_list] == ["ou_A"]
    out = resolve_mentions(
        "hey @_user_1 @_user_2 how are you",
        ext,
        strip_bot_mentions=True,
        bot_open_id="ou_bot",
    )
    assert "@_user_1" not in out
    assert "@Alice" in out


def test_parse_at_tags_extracts():
    ms, all_, stripped = parse_at_tags('hello <at user_id="ou_x">Alice</at>!')
    assert all_ is False
    assert "@Alice" in stripped
    assert len(ms) == 1
    assert ms[0].open_id == "ou_x"
    assert ms[0].name == "Alice"


def test_parse_at_tags_mentioned_all():
    ms, all_, stripped = parse_at_tags('<at user_id="all">everyone</at> notice')
    assert all_ is True
    assert "@all" in stripped
    assert ms == []


# ---------------------------------------------------------------------------
# Regression: Feishu ships mention-all as a bare ``@_all`` token in text
# content with ``mentions=null``. Detection must come from the text, not
# just the mentions array.
# ---------------------------------------------------------------------------


def test_text_has_mention_all_detects_bare_token():
    assert text_has_mention_all("@_all please ack") is True
    assert text_has_mention_all("prefix @_all suffix") is True
    assert text_has_mention_all("@_all") is True


def test_text_has_mention_all_false_for_non_token_substring():
    # Guard against false positives where ``@_all`` is a prefix of a
    # different identifier.
    assert text_has_mention_all("@_all_employees please ack") is False
    assert text_has_mention_all("@_allhands meeting") is False
    assert text_has_mention_all("") is False
    assert text_has_mention_all(None) is False


def test_resolve_mentions_rewrites_at_all_placeholder():
    """User-visible content shouldn't leak the raw ``@_all`` token."""
    result = resolve_mentions("@_all hi", extract_mentions([]))
    assert result == "@all hi"
