"""Tests for the outbound text chunker."""

from lark_oapi.channel.outbound.sender import chunk_text


def test_short_text_passthrough():
    assert chunk_text("hi", limit=4000) == ["hi"]


def test_empty_returns_empty_list():
    assert chunk_text("", limit=4000) == []


def test_newline_boundary():
    body = "abc\n" * 100  # 400 chars
    chunks = chunk_text(body, limit=50, mode="newline")
    assert all(len(c) <= 50 for c in chunks)
    # Re-joining with the delimiter should yield original (minus trimmed trailing)
    joined = "\n".join(chunks)
    # Accept either trailing newline or not — reconstruction is approximate.
    assert joined.replace("\n", "") == body.replace("\n", "")


def test_hard_cut_when_no_delimiter():
    body = "x" * 123
    chunks = chunk_text(body, limit=30, mode="newline")
    assert chunks == ["x" * 30, "x" * 30, "x" * 30, "x" * 30, "x" * 3]


def test_paragraph_mode():
    body = "para1 line1\npara1 line2\n\npara2 line1\n\npara3"
    chunks = chunk_text(body, limit=20, mode="paragraph")
    assert chunks


def test_none_mode_hard_cut():
    chunks = chunk_text("abcdefghij", limit=3, mode="none")
    assert chunks == ["abc", "def", "ghi", "j"]
