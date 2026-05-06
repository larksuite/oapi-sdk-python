"""Card builder tests."""

from lark_oapi.channel.card.builder import card


def test_minimal_card():
    c = card().markdown("hi").build()
    assert c.version == "v2"
    assert c.data["schema"] == "2.0"
    assert c.data["body"]["elements"][0] == {"tag": "markdown", "content": "hi"}


def test_header():
    c = card().header(title="H", subtitle="sub", template="blue").markdown("x").build()
    assert c.data["header"]["title"]["content"] == "H"
    assert c.data["header"]["subtitle"]["content"] == "sub"
    assert c.data["header"]["template"] == "blue"


def test_button_emitted_as_top_level_v2():
    c = (
        card()
        .button(label="Approve", action={"type": "approve"}, style="primary")
        .build()
    )
    el = c.data["body"]["elements"][0]
    # CardKit v2 dropped the `action` wrapper — button is top-level
    assert el["tag"] == "button"
    assert el["type"] == "primary"
    assert el["value"] == {"type": "approve"}
    assert el["text"]["content"] == "Approve"


def test_divider_and_image():
    c = card().divider().image("img_x", alt="A").build()
    body = c.data["body"]["elements"]
    assert body[0]["tag"] == "hr"
    assert body[1]["tag"] == "img"
    assert body[1]["img_key"] == "img_x"


def test_raw_passthrough():
    c = card().raw({"tag": "custom_element", "payload": 1}).build()
    assert c.data["body"]["elements"][0] == {"tag": "custom_element", "payload": 1}


def test_column_set_embeds_subbuilder_elements():
    col = card().markdown("a")
    col2 = card().markdown("b")
    c = card().column_set([col, col2]).build()
    cs = c.data["body"]["elements"][0]
    assert cs["tag"] == "column_set"
    assert len(cs["columns"]) == 2
    assert cs["columns"][0]["elements"][0]["content"] == "a"


def test_progress_bar_renders_percent():
    c = card().progress(42, label="Deploying").build()
    md = c.data["body"]["elements"][0]["content"]
    assert "42%" in md


def test_streaming_flag_sets_config():
    c = card().streaming(True).markdown("...").build()
    assert c.data["config"].get("streaming_mode") is True


def test_table_emits_native_table_component():
    # Previously `.table()` stuffed a GFM pipe-table into a markdown element
    # where Feishu silently drops pipe syntax. It must now emit the native
    # Card 2.0 `table` component.
    c = card().table(
        headers=["Name", "Score"],
        rows=[["Alice", "90"], ["Bob", "80"]],
    ).build()
    el = c.data["body"]["elements"][0]
    assert el["tag"] == "table"
    assert el["columns"] == [
        {"name": "col_0", "display_name": "Name", "data_type": "text"},
        {"name": "col_1", "display_name": "Score", "data_type": "text"},
    ]
    assert el["rows"] == [
        {"col_0": "Alice", "col_1": "90"},
        {"col_0": "Bob", "col_1": "80"},
    ]


def test_table_auto_picks_lark_md_for_inline_markdown():
    c = card().table(
        headers=["Name", "Status"],
        rows=[["**Alice**", "ok"], ["Bob", "`done`"]],
    ).build()
    cols = c.data["body"]["elements"][0]["columns"]
    assert cols[0]["data_type"] == "lark_md"  # **Alice**
    assert cols[1]["data_type"] == "lark_md"  # `done`


def test_table_pads_short_rows_and_clamps_page_size():
    c = card().table(
        headers=["a", "b", "c"],
        rows=[["1"], ["2", "3", "4", "5"]],
        page_size=99,
    ).build()
    el = c.data["body"]["elements"][0]
    assert el["page_size"] == 10
    assert el["rows"] == [
        {"col_0": "1", "col_1": "", "col_2": ""},
        {"col_0": "2", "col_1": "3", "col_2": "4"},
    ]


def test_table_rejects_mismatched_data_types():
    import pytest
    with pytest.raises(ValueError):
        card().table(
            headers=["a", "b"],
            rows=[["1", "2"]],
            data_types=["text"],
        )
