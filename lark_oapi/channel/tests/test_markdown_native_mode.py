"""tag_md_mode behavior tests."""
import json
from dataclasses import fields
from pathlib import Path

import pytest

from lark_oapi.channel.config import MarkdownConverter, OutboundConfig
from lark_oapi.channel.outbound.markdown.to_post import (
    _split_at_code_fences,
    markdown_to_post_ast,
)

# Fixture set covering structured and native markdown conversion.
FIXTURES = {
    "01_plain": "这是普通文本，没有任何 markdown。",
    "02_bold": "下面是 **粗体** 文字。",
    "03_italic": "下面是 *斜体* 文字。",
    "04_bold_italic": "组合 ***粗+斜*** 看一下。",
    "05_h1": "# H1 标题（应该字号最大）",
    "06_h2": "## H2 标题（中号）",
    "07_h3": "### H3 标题（小号）",
    "08_quote": "> 这是引用块第一行\n> 引用块第二行",
    "09_nested_quote": "> 外层引用\n>> 嵌套引用",
    "10_ul": "- 苹果\n- 香蕉\n- 樱桃",
    "11_ol": "1. 第一\n2. 第二\n3. 第三",
    "12_nested_ul": "- 顶层\n  - 子项 1\n  - 子项 2",
    "13_inline_code": "命令是 `git status` 用来查看状态。",
    "14_link": "查看 [文档](https://example.com) 了解更多。",
    "15_code_fence": "```python\nprint('hi')\n```",
    "16_composite": (
        "# 标题\n\n"
        "**重点**：下面是清单。\n\n"
        "- a\n- b\n\n"
        "> 引用\n\n"
        "```python\nprint('done')\n```"
    ),
}


def test_markdown_converter_has_tag_md_mode_field_with_structured_default():
    conv = MarkdownConverter()
    assert conv.tag_md_mode == "structured"


def test_markdown_converter_accepts_native_tag_md_mode():
    conv = MarkdownConverter(tag_md_mode="native")
    assert conv.tag_md_mode == "native"


def test_markdown_converter_field_order_appends_new_field_at_end():
    # New fields must be appended so positional kwargs in existing call sites
    # keep working.
    names = [f.name for f in fields(MarkdownConverter)]
    assert names[:2] == ["enabled", "table_mode"]
    assert names[-1] == "tag_md_mode"


class TestSplitAtCodeFences:
    def test_empty_string_returns_empty_list(self):
        assert _split_at_code_fences("") == []

    def test_plain_text_is_single_segment(self):
        assert _split_at_code_fences("hello world") == ["hello world"]

    def test_text_with_one_fence_splits_into_three_segments(self):
        text = "before\n```python\nprint('hi')\n```\nafter"
        out = _split_at_code_fences(text)
        # prose before, the fenced block (open+body+close), prose after
        assert len(out) == 3
        assert out[0] == "before"
        assert out[1] == "```python\nprint('hi')\n```"
        assert out[2] == "after"

    def test_text_starting_with_fence_no_leading_prose_segment(self):
        text = "```\ncode\n```\ntrailing"
        out = _split_at_code_fences(text)
        assert out == ["```\ncode\n```", "trailing"]

    def test_text_ending_with_fence_no_trailing_prose_segment(self):
        text = "leading\n```\ncode\n```"
        out = _split_at_code_fences(text)
        assert out == ["leading", "```\ncode\n```"]

    def test_only_fence_block(self):
        text = "```python\nprint('x')\n```"
        assert _split_at_code_fences(text) == ["```python\nprint('x')\n```"]

    def test_unclosed_fence_treated_as_text(self):
        # Defensive: if no closing fence, the rest of the text is one segment
        # (don't drop content).
        text = "before\n```python\nstill open"
        out = _split_at_code_fences(text)
        assert "".join(out).count("```") == 1
        assert "still open" in out[-1]

    def test_two_fences_separated_by_prose(self):
        text = "a\n```\nx\n```\nb\n```\ny\n```\nc"
        out = _split_at_code_fences(text)
        assert out == [
            "a",
            "```\nx\n```",
            "b",
            "```\ny\n```",
            "c",
        ]


class TestNativeMode:
    def test_plain_text_native_returns_single_md_node(self):
        out = markdown_to_post_ast("hello world", tag_md_mode="native")
        assert out == {
            "zh_cn": {
                "title": "",
                "content": [[{"tag": "md", "text": "hello world"}]],
            }
        }

    def test_header_native_wraps_raw(self):
        out = markdown_to_post_ast("# Hello", tag_md_mode="native")
        assert out["zh_cn"]["content"] == [[{"tag": "md", "text": "# Hello"}]]

    def test_blockquote_native_wraps_raw(self):
        out = markdown_to_post_ast("> quote", tag_md_mode="native")
        assert out["zh_cn"]["content"] == [[{"tag": "md", "text": "> quote"}]]

    def test_code_fence_native_produces_at_least_two_rows(self):
        text = "# H1\n\n```python\nprint('hi')\n```"
        out = markdown_to_post_ast(text, tag_md_mode="native")
        rows = out["zh_cn"]["content"]
        assert len(rows) >= 2
        # Every node in every row must be tag:md
        for row in rows:
            for node in row:
                assert node["tag"] == "md", f"got non-md node: {node}"
        # The fence segment must be one row, intact
        fence_rows = [r for r in rows if "```" in r[0]["text"]]
        assert len(fence_rows) == 1
        assert fence_rows[0][0]["text"] == "```python\nprint('hi')\n```"

    def test_native_mode_no_structured_nodes_for_all_fixtures(self):
        for label, text in FIXTURES.items():
            out = markdown_to_post_ast(text, tag_md_mode="native")
            for row in out["zh_cn"]["content"]:
                for node in row:
                    assert node["tag"] == "md", (
                        f"fixture {label!r} produced non-md node: {node}"
                    )

    def test_native_mode_title_propagated(self):
        out = markdown_to_post_ast("body", title="My Title", tag_md_mode="native")
        assert out["zh_cn"]["title"] == "My Title"

    def test_native_mode_locale_propagated(self):
        out = markdown_to_post_ast("body", locale="en_us", tag_md_mode="native")
        assert "en_us" in out

    def test_empty_input_native_returns_valid_structure(self):
        out = markdown_to_post_ast("", tag_md_mode="native")
        rows = out["zh_cn"]["content"]
        assert isinstance(rows, list)


class TestStructuredSnapshot:
    """Structured-mode output must stay byte-identical to the snapshot."""

    @staticmethod
    def _load_snapshot():
        path = Path(__file__).parent / "snapshots" / "markdown_structured.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_structured_default_kwarg_equals_snapshot(self):
        snapshot = self._load_snapshot()
        for label, text in FIXTURES.items():
            actual = markdown_to_post_ast(text)
            assert actual == snapshot[label], (
                f"structured-mode regression for {label!r}\n"
                f"expected: {json.dumps(snapshot[label], ensure_ascii=False)}\n"
                f"actual:   {json.dumps(actual, ensure_ascii=False)}"
            )

    def test_structured_explicit_kwarg_equals_default(self):
        for label, text in FIXTURES.items():
            assert markdown_to_post_ast(text) == markdown_to_post_ast(
                text, tag_md_mode="structured"
            ), f"explicit and default disagree for {label!r}"


class TestSenderBuildPost:
    def test_build_post_default_uses_structured(self):
        from lark_oapi.channel.outbound.sender import _build_post
        from lark_oapi.channel.types import OutboundPost

        msg = OutboundPost(markdown="# Hello")
        body = _build_post(msg)
        content = json.loads(body["content"])
        node = content["zh_cn"]["content"][0][0]
        assert node["tag"] == "text"
        assert "bold" in node.get("style", [])

    def test_build_post_native_returns_tag_md(self):
        from lark_oapi.channel.outbound.sender import _build_post
        from lark_oapi.channel.types import OutboundPost

        msg = OutboundPost(markdown="# Hello")
        body = _build_post(msg, tag_md_mode="native")
        content = json.loads(body["content"])
        node = content["zh_cn"]["content"][0][0]
        assert node == {"tag": "md", "text": "# Hello"}

    def test_build_post_opaque_pass_through_ignores_tag_md_mode(self):
        from lark_oapi.channel.outbound.sender import _build_post
        from lark_oapi.channel.types import OutboundPost

        ast = {"zh_cn": {"title": "", "content": [[{"tag": "text", "text": "x"}]]}}
        msg = OutboundPost(post=ast)
        body_default = _build_post(msg)
        body_native = _build_post(msg, tag_md_mode="native")
        assert body_default == body_native
        assert json.loads(body_default["content"]) == ast


class TestEnabledPriority:
    """enabled=False overrides tag_md_mode=native."""

    def test_disabled_converter_branch_picks_structured(self):
        # Replicate the sender's branch logic exactly:
        conv = MarkdownConverter(enabled=False, tag_md_mode="native")
        if getattr(conv, "enabled", True):
            tag_md_mode = getattr(conv, "tag_md_mode", "structured")
        else:
            tag_md_mode = "structured"
        assert tag_md_mode == "structured"

    def test_disabled_converter_via_sender_uses_structured(self):
        # Even when MarkdownConverter is configured with native, disabling
        # the converter forces structured (plain-text fallback) at _materialize.
        from lark_oapi.channel.config import OutboundConfig
        from lark_oapi.channel.outbound.sender import OutboundSender
        from lark_oapi.channel.tests.test_sender import make_driver
        from lark_oapi.channel.types import OutboundPost

        async def _run():
            d, calls = make_driver()
            cfg = OutboundConfig(
                markdown_converter=MarkdownConverter(
                    enabled=False, tag_md_mode="native",
                ),
            )
            s = OutboundSender(d, cfg)
            await s.send(OutboundPost(markdown="# Hello"), receive_id="oc_x")
            content = json.loads(calls[0]["content"])
            node = content["zh_cn"]["content"][0][0]
            # enabled=False -> structured path, header collapses to bold tag:text
            assert node["tag"] == "text"
            assert "bold" in node.get("style", [])

        import asyncio
        asyncio.run(_run())


class TestSenderEndToEndNativeMode:
    """Sender plumbing produces tag:md when configured with native mode."""

    @pytest.mark.asyncio
    async def test_outbound_post_native_produces_tag_md_only_payload(self):
        from lark_oapi.channel.outbound.sender import OutboundSender
        from lark_oapi.channel.tests.test_sender import make_driver
        from lark_oapi.channel.types import OutboundPost

        d, calls = make_driver()
        cfg = OutboundConfig(
            markdown_converter=MarkdownConverter(tag_md_mode="native"),
        )
        s = OutboundSender(d, cfg)
        await s.send(
            OutboundPost(markdown="# Hello\n\n- a\n- b"),
            receive_id="oc_x",
        )
        assert calls[0]["msg_type"] == "post"
        content = json.loads(calls[0]["content"])
        for row in content["zh_cn"]["content"]:
            for node in row:
                assert node["tag"] == "md", f"non-md node leaked: {node}"

    @pytest.mark.asyncio
    async def test_outbound_post_default_still_produces_structured_payload(self):
        from lark_oapi.channel.outbound.sender import OutboundSender
        from lark_oapi.channel.tests.test_sender import make_driver
        from lark_oapi.channel.types import OutboundPost

        d, calls = make_driver()
        s = OutboundSender(d)  # default OutboundConfig: structured
        await s.send(OutboundPost(markdown="# Hello"), receive_id="oc_x")
        content = json.loads(calls[0]["content"])
        node = content["zh_cn"]["content"][0][0]
        assert node["tag"] == "text"
        assert "bold" in node.get("style", [])

    @pytest.mark.asyncio
    async def test_outbound_post_native_with_code_fence_produces_multi_row(self):
        from lark_oapi.channel.config import OutboundConfig
        from lark_oapi.channel.outbound.sender import OutboundSender
        from lark_oapi.channel.tests.test_sender import make_driver
        from lark_oapi.channel.types import OutboundPost

        d, calls = make_driver()
        cfg = OutboundConfig(
            markdown_converter=MarkdownConverter(tag_md_mode="native"),
        )
        s = OutboundSender(d, cfg)
        await s.send(
            OutboundPost(markdown="# H1\n\n```python\nprint('hi')\n```"),
            receive_id="oc_x",
        )
        content = json.loads(calls[0]["content"])
        rows = content["zh_cn"]["content"]
        assert len(rows) >= 2
        fence_rows = [r for r in rows if "```" in r[0]["text"]]
        assert len(fence_rows) == 1
