"""Tests for flat-string content + resources[] derivation (Node-aligned)."""

from lark_oapi.channel.normalize.flatten import flatten
from lark_oapi.channel.types import (
    AudioContent,
    FileContent,
    FolderContent,
    GeneralCalendarContent,
    HongbaoContent,
    ImageContent,
    InteractiveContent,
    LocationContent,
    MediaContent,
    MergeForwardContent,
    MergeForwardItem,
    PostContent,
    ShareCalendarEventContent,
    ShareChatContent,
    ShareUserContent,
    StickerContent,
    TextContent,
    UnknownContent,
)


def test_text_flat_passthrough():
    t, r = flatten(TextContent(text="hello"))
    assert t == "hello" and r == []


def test_image_markdown_placeholder_plus_resource():
    t, r = flatten(ImageContent(image_key="img_abc"))
    assert t == "![image](img_abc)"
    assert len(r) == 1
    assert r[0].type == "image" and r[0].file_key == "img_abc"


def test_file_xml_placeholder_resource_has_name():
    t, r = flatten(FileContent(file_key="f_x", file_name="report.pdf"))
    assert "key=\"f_x\"" in t and "report.pdf" in t
    assert r[0].type == "file" and r[0].file_name == "report.pdf"


def test_video_uses_media_content_with_cover():
    t, r = flatten(MediaContent(file_key="v_1", image_key="cov_1", duration_ms=3000))
    assert "<video " in t and 'key="v_1"' in t
    assert r[0].type == "video" and r[0].cover_image_key == "cov_1"


def test_audio_and_sticker_emit_resource():
    _, ra = flatten(AudioContent(file_key="a_1", duration_ms=1500))
    assert ra[0].type == "audio" and ra[0].duration_ms == 1500
    _, rs = flatten(StickerContent(file_key="s_1"))
    assert rs[0].type == "sticker"


def test_share_chat_and_user_emit_tag_only():
    t, _ = flatten(ShareChatContent(chat_id="oc_123"))
    assert "<group_card" in t and "oc_123" in t
    t, _ = flatten(ShareUserContent(user_id="ou_456"))
    assert "<contact_card" in t


def test_location_tag():
    t, _ = flatten(LocationContent(name="HQ", longitude=116.4, latitude=39.9))
    assert "<location" in t and "HQ" in t


def test_folder_hongbao_tags():
    # Folder requires a file_key (node-aligned); falls back to [folder] without one.
    assert "<folder" in flatten(FolderContent(file_key="fk_1", file_name="docs"))[0]
    assert "[folder]" == flatten(FolderContent(file_name="docs"))[0]
    assert "<hongbao" in flatten(HongbaoContent(text="新年快乐"))[0]


def test_general_calendar_and_share_calendar_event():
    # Node-aligned tags: GeneralCalendar → <calendar>, ShareCalendarEvent → <calendar_share>.
    assert "<calendar>" in flatten(GeneralCalendarContent(summary="Sync"))[0]
    assert "<calendar_share>" in flatten(
        ShareCalendarEventContent(summary="Demo", organizer="Alice")
    )[0]


def test_post_to_markdown_style_mapping():
    post = {
        "zh_cn": {
            "title": "Title",
            "content": [
                [
                    {"tag": "text", "text": "bold bit", "style": ["bold"]},
                    {"tag": "text", "text": " normal "},
                    {"tag": "a", "text": "link", "href": "https://x"},
                ],
                [{"tag": "code_block", "language": "python", "text": "print(1)"}],
            ],
        }
    }
    t, _ = flatten(PostContent(post=post))
    assert "# Title" in t
    assert "**bold bit**" in t
    assert "[link](https://x)" in t
    assert "```python" in t


def test_post_resources_include_images_media_audio_and_files_deduped():
    post = {
        "zh_cn": {
            "title": "Assets",
            "content": [
                [
                    {"tag": "text", "text": "see "},
                    {"tag": "img", "image_key": "img_1"},
                    {"tag": "img", "image_key": "img_1"},
                    {"tag": "media", "file_key": "vid_1"},
                ],
                [
                    {"tag": "audio", "file_key": "aud_1"},
                    {"tag": "file", "file_key": "file_1", "file_name": "report.pdf"},
                ],
            ],
        }
    }

    t, r = flatten(PostContent(post=post))

    assert "![image](img_1)" in t
    assert "[media:vid_1]" in t
    assert [(x.type, x.file_key, x.file_name) for x in r] == [
        ("image", "img_1", None),
        ("video", "vid_1", None),
        ("audio", "aud_1", None),
        ("file", "file_1", "report.pdf"),
    ]


def test_post_direct_document_shape_flattens_text_and_resources():
    post = {
        "title": "Direct",
        "content": [
            [
                {"tag": "text", "text": "hello "},
                {"tag": "a", "text": "link", "href": "https://x"},
                {"tag": "img", "image_key": "img_direct"},
            ]
        ],
    }

    t, r = flatten(PostContent(post=post))

    assert "# Direct" in t
    assert "[link](https://x)" in t
    assert r[0].type == "image"
    assert r[0].file_key == "img_direct"


def test_merge_forward_flatten_recursive():
    child = TextContent(text="child content")
    item = MergeForwardItem(
        message_id="c1",
        sender_name="Alice",
        create_time=int(__import__("time").time() * 1000),
        content=child,
    )
    content = MergeForwardContent(loading=False, items=[item])
    t, r = flatten(content)
    assert "<forwarded_messages>" in t
    assert "Alice:" in t
    assert "child content" in t


def test_interactive_walk_picks_markdown_leaves():
    card = {
        "schema": "2.0",
        "header": {
            "title": {"tag": "plain_text", "content": "Header"},
            "subtitle": {"tag": "plain_text", "content": "sub"},
        },
        "body": {
            "elements": [
                {"tag": "markdown", "content": "body1"},
                {"tag": "column_set", "columns": [
                    {"tag": "column", "elements": [
                        {"tag": "markdown", "content": "in column"},
                    ]},
                ]},
            ],
        },
    }
    t, _ = flatten(InteractiveContent(card=card, card_version="v2"))
    for expected in ["Header", "body1", "in column"]:
        assert expected in t


def test_unknown_fallback_uses_raw_text():
    t, _ = flatten(UnknownContent(raw={"text": "raw text"}))
    assert t == "raw text"
    t, _ = flatten(UnknownContent(raw={}))
    assert t == "[unsupported message]"
