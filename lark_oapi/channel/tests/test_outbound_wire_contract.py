"""Byte-level contract tests for the outbound ``_build_*`` helpers.

These tests assert the EXACT JSON shape Feishu's
``POST /open-apis/im/v1/messages`` expects for each ``msg_type``. They are
designed to catch a class of bug where Python's SDK produces structurally
plausible output but wraps or key-names differ from what the server accepts
— e.g. the 2024 ``230001 invalid message content`` incident caused by
wrapping post content with an extra ``{"post": ...}`` envelope.

Reference shapes (verified against Feishu OpenAPI docs + node-sdk):

    text       → ``{"text": "..."}``
    post       → ``{"<locale>": {"title": "...", "content": [[...]]}}``  (NO outer "post")
    interactive→ card JSON as-is   OR  ``{"type": "card", "data": {"card_id": "..."}}``
    image      → ``{"image_key": "..."}``
    file       → ``{"file_key": "..."}``
    audio      → ``{"file_key": "..."}``
    media      → ``{"file_key": "..."}``  (msg_type is "media", not "video")
"""

import json

from lark_oapi.channel.outbound.sender import (
    _build_audio,
    _build_card,
    _build_file,
    _build_image,
    _build_post,
    _build_text,
    _build_video,
    _post_to_plain_text_from_body,
)
from lark_oapi.channel.types import (
    Identity,
    OutboundCard,
    OutboundPost,
    OutboundText,
)


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------


def test_text_wire_shape_is_bare_text_object():
    body = _build_text(OutboundText(text="hello"))
    assert body["msg_type"] == "text"
    parsed = json.loads(body["content"])
    assert parsed == {"text": "hello"}


def test_text_wire_mention_prepends_at_tag():
    body = _build_text(
        OutboundText(
            text="ping",
            mentions=[Identity(open_id="ou_alice", display_name="Alice")],
        )
    )
    parsed = json.loads(body["content"])
    # `<at user_id="ou_alice">Alice</at> ping`
    assert parsed["text"].startswith('<at user_id="ou_alice">Alice</at>')
    assert parsed["text"].endswith("ping")


# ---------------------------------------------------------------------------
# post — the shape that caused 230001 in production
# ---------------------------------------------------------------------------


def test_post_content_is_locale_map_not_wrapped():
    body = _build_post(OutboundPost(markdown="**bold**"))
    assert body["msg_type"] == "post"
    parsed = json.loads(body["content"])
    # REGRESSION: Feishu API rejects content wrapped as {"post": {...}}.
    # Correct shape is the locale-keyed map directly at the root.
    assert "post" not in parsed, (
        f"post content must NOT be wrapped in {{'post': ...}}; got keys {list(parsed)}"
    )
    assert "zh_cn" in parsed
    assert "title" in parsed["zh_cn"]
    assert "content" in parsed["zh_cn"]
    assert isinstance(parsed["zh_cn"]["content"], list)
    assert isinstance(parsed["zh_cn"]["content"][0], list)


def test_post_with_prebuilt_ast_not_wrapped():
    ast = {
        "zh_cn": {
            "title": "hello",
            "content": [[{"tag": "text", "text": "world"}]],
        }
    }
    body = _build_post(OutboundPost(post=ast))
    parsed = json.loads(body["content"])
    assert parsed == ast  # exact equality — not wrapped


def test_post_empty_still_unwrapped():
    body = _build_post(OutboundPost(title="x"))
    parsed = json.loads(body["content"])
    assert "post" not in parsed
    assert parsed["zh_cn"]["title"] == "x"


def test_post_body_plain_text_fallback_reads_unwrapped_shape():
    # Simulates the format_error → plain-text downgrade path.
    body = _build_post(OutboundPost(markdown="**hi**"))
    plain = _post_to_plain_text_from_body(body["content"])
    # Round-trip through the fallback recovers the text — proving it reads
    # the same unwrapped shape that _build_post emits.
    assert "hi" in plain


# ---------------------------------------------------------------------------
# card (interactive)
# ---------------------------------------------------------------------------


def test_card_raw_card_shape_passthrough():
    raw = {"schema": "2.0", "body": {"elements": [{"tag": "markdown", "content": "x"}]}}
    body = _build_card(OutboundCard(card=raw))
    assert body["msg_type"] == "interactive"
    assert json.loads(body["content"]) == raw


def test_card_by_id_shape_is_type_card_data_card_id():
    body = _build_card(OutboundCard(card_id="cd_abc"))
    assert body["msg_type"] == "interactive"
    assert json.loads(body["content"]) == {"type": "card", "data": {"card_id": "cd_abc"}}


# ---------------------------------------------------------------------------
# media builders
# ---------------------------------------------------------------------------


def test_image_shape_is_image_key_only():
    body = _build_image("img_abc")
    assert body["msg_type"] == "image"
    assert json.loads(body["content"]) == {"image_key": "img_abc"}


def test_file_shape_is_file_key_only():
    body = _build_file("file_abc")
    assert body["msg_type"] == "file"
    assert json.loads(body["content"]) == {"file_key": "file_abc"}


def test_audio_shape_is_file_key_only():
    body = _build_audio("file_audio")
    assert body["msg_type"] == "audio"
    assert json.loads(body["content"]) == {"file_key": "file_audio"}


def test_video_uses_media_msg_type_and_file_key():
    # Feishu distinguishes video upload via msg_type="media".
    body = _build_video("file_video")
    assert body["msg_type"] == "media"
    assert json.loads(body["content"]) == {"file_key": "file_video"}
