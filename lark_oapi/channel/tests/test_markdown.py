"""Tests for the Markdown → post AST converter."""

from lark_oapi.channel.outbound.markdown import markdown_to_post_ast
from lark_oapi.channel.types import Identity


def _zh(ast):
    return ast["zh_cn"]


def test_plain_paragraph():
    ast = markdown_to_post_ast("hello world")
    assert _zh(ast)["title"] == ""
    paras = _zh(ast)["content"]
    assert paras == [[{"tag": "text", "text": "hello world"}]]


def test_heading_becomes_bold_text():
    ast = markdown_to_post_ast("# Title\n\nbody")
    paras = _zh(ast)["content"]
    assert paras[0][0]["style"] == ["bold"] and paras[0][0]["text"] == "Title"
    assert paras[1] == [{"tag": "text", "text": "body"}]


def test_bold_italic_code_inline():
    ast = markdown_to_post_ast("**bold** and *it* and `code`")
    paras = _zh(ast)["content"]
    runs = paras[0]
    styles = [(r.get("text"), r.get("style", [])) for r in runs if r["tag"] == "text"]
    assert ("bold", ["bold"]) in styles
    assert ("it", ["italic"]) in styles
    assert ("code", ["code"]) in styles


def test_link_emits_a_tag():
    ast = markdown_to_post_ast("see [docs](https://x.example)")
    runs = _zh(ast)["content"][0]
    a_tag = next(r for r in runs if r["tag"] == "a")
    assert a_tag["text"] == "docs"
    assert a_tag["href"] == "https://x.example"


def test_code_block_fenced():
    ast = markdown_to_post_ast("```python\nprint(1)\n```")
    paras = _zh(ast)["content"]
    cb = paras[0][0]
    assert cb["tag"] == "code_block"
    assert cb["language"] == "PYTHON"
    assert cb["text"] == "print(1)"


def test_bullet_list_each_paragraph():
    ast = markdown_to_post_ast("- one\n- two\n- three")
    paras = _zh(ast)["content"]
    assert len(paras) == 3
    assert paras[0][0]["text"].startswith("• one")


def test_hr():
    ast = markdown_to_post_ast("top\n\n---\n\nbot")
    paras = _zh(ast)["content"]
    assert any(p == [{"tag": "hr"}] for p in paras)


def test_blockquote_marker():
    ast = markdown_to_post_ast("> quoted line")
    first = _zh(ast)["content"][0]
    assert first[0] == {"tag": "text", "text": "│ "}


def test_mentions_injected():
    ast = markdown_to_post_ast(
        "hi",
        mentions=[Identity(open_id="ou_1", display_name="Alice")],
    )
    first = _zh(ast)["content"][0]
    # First run is the <at> tag
    assert first[0]["tag"] == "at"
    assert first[0]["user_id"] == "ou_1"
    assert first[0]["user_name"] == "Alice"


def test_table_mode_bullets():
    md = "| name | age |\n|---|---|\n| Alice | 30 |\n| Bob | 25 |"
    ast = markdown_to_post_ast(md, table_mode="bullets")
    paras = _zh(ast)["content"]
    assert paras[0][0]["text"].startswith("• name: Alice")
    assert paras[1][0]["text"].startswith("• name: Bob")


def test_empty_input_yields_empty_paragraph():
    ast = markdown_to_post_ast("")
    assert _zh(ast)["content"] == [[]] or _zh(ast)["content"] == [[{"tag": "text", "text": ""}]]
