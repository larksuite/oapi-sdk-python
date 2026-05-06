"""Byte-level output alignment with node-sdk converters.

Every assertion here corresponds to a node-sdk converter's observable output
format (tag names, indentation, emoji prefixes, attribute names). Divergence
caught here = a regression that node users would see differently from
Python users.

Node source reference (commit ccc7e31):
    https://github.com/larksuite/node-sdk/tree/ccc7e31/channel/normalize/converters
"""

from lark_oapi.channel.normalize.converters import (
    calendar as calendar_c,
    folder as folder_c,
    merge_forward as mf_c,
    share as share_c,
    system as system_c,
    todo as todo_c,
    video_chat as vc_c,
    vote as vote_c,
)
from lark_oapi.channel.types import (
    CalendarContent,
    FolderContent,
    GeneralCalendarContent,
    MergeForwardContent,
    MergeForwardItem,
    ShareCalendarEventContent,
    ShareChatContent,
    ShareUserContent,
    SystemContent,
    TextContent,
    TodoContent,
    VideoChatContent,
    VoteContent,
)


# ---- system: template regex expansion ---------------------------------------


def test_system_expands_template_variables():
    content = SystemContent(
        template="{from_user} invited {to_chatters}",
        raw={
            "template": "{from_user} invited {to_chatters}",
            "from_user": [{"name": "Alice"}],
            "to_chatters": [{"name": "Bob"}, {"name": "Carol"}],
        },
    )
    text, _ = system_c.convert(content)
    assert text == "Alice invited Bob, Carol"


def test_system_missing_template_emits_placeholder():
    text, _ = system_c.convert(SystemContent(template=""))
    assert text == "[system message]"


def test_system_unknown_key_becomes_empty():
    # Node's policy: unknown key → empty string (matches `val == null` branch
    # in node's system.ts). Trailing whitespace is trimmed.
    content = SystemContent(template="Hi {unknown}", raw={"template": "Hi {unknown}"})
    text, _ = system_c.convert(content)
    assert text == "Hi"


def test_system_non_string_value_preserves_placeholder():
    # Node's policy: if value is neither string/array/null, leave the
    # placeholder as-is (fallthrough `return match`).
    content = SystemContent(
        template="Count: {n}",
        raw={"template": "Count: {n}", "n": 42},  # int, not str
    )
    text, _ = system_c.convert(content)
    assert text == "Count: {n}"


# ---- todo: rich multi-line output -------------------------------------------


def test_todo_with_title_body_due_formats_multiline():
    content = TodoContent(title="Ship it", body="before EOD", due_time=1700000000000)
    text, _ = todo_c.convert(content)
    assert text.startswith("<todo>\n")
    assert text.endswith("\n</todo>")
    assert "Ship it" in text
    assert "before EOD" in text
    assert "Due: " in text


def test_todo_empty_emits_placeholder():
    text, _ = todo_c.convert(TodoContent())
    assert text == "<todo>\n[todo]\n</todo>"


# ---- video_chat: <meeting> block with emoji + time --------------------------


def test_video_chat_renders_meeting_block():
    content = VideoChatContent(topic="Sprint Planning", start_time=1700000000000)
    text, _ = vc_c.convert(content)
    assert text.startswith("<meeting>\n")
    assert text.endswith("\n</meeting>")
    assert "📹 Sprint Planning" in text
    assert "🕙 " in text


def test_video_chat_empty_emits_placeholder():
    text, _ = vc_c.convert(VideoChatContent())
    assert text == "<meeting>\n[video chat]\n</meeting>"


# ---- calendar (3 variants): rich block + correct tag names ------------------


def test_calendar_invite_tag_name():
    content = CalendarContent(summary="Sync", start_time=1700000000000)
    text, _ = calendar_c.convert(content)
    assert text.startswith("<calendar_invite>\n")
    assert text.endswith("\n</calendar_invite>")
    assert "📅 Sync" in text


def test_general_calendar_tag_name_is_calendar():
    content = GeneralCalendarContent(summary="Demo")
    text, _ = calendar_c.convert_general(content)
    assert text.startswith("<calendar>\n")
    assert text.endswith("\n</calendar>")
    assert "📅 Demo" in text


def test_share_calendar_event_tag_name_is_calendar_share():
    content = ShareCalendarEventContent(summary="Demo")
    text, _ = calendar_c.convert_share_event(content)
    assert text.startswith("<calendar_share>\n")
    assert text.endswith("\n</calendar_share>")


def test_calendar_start_end_rendered_with_tilde():
    content = CalendarContent(
        summary="Mtg", start_time=1700000000000, end_time=1700003600000
    )
    text, _ = calendar_c.convert(content)
    assert "~" in text


# ---- vote: multi-line bullets -----------------------------------------------


def test_vote_multiline_with_bullet_options():
    content = VoteContent(topic="Lunch?", options=["Pizza", "Sushi"])
    text, _ = vote_c.convert(content)
    lines = text.split("\n")
    assert lines[0] == "<vote>"
    assert "Lunch?" in lines
    assert "• Pizza" in lines
    assert "• Sushi" in lines
    assert lines[-1] == "</vote>"


def test_vote_empty_placeholder():
    text, _ = vote_c.convert(VoteContent())
    assert text == "<vote>\n[vote]\n</vote>"


# ---- share: id= attribute (not chat_id= / user_id=) -------------------------


def test_share_chat_uses_id_attribute():
    text, _ = share_c.convert_chat(ShareChatContent(chat_id="oc_123"))
    assert text == '<group_card id="oc_123"/>'


def test_share_user_uses_id_attribute():
    text, _ = share_c.convert_user(ShareUserContent(user_id="ou_456"))
    assert text == '<contact_card id="ou_456"/>'


# ---- folder: key= attribute + optional name= ------------------------------


def test_folder_with_key_and_name():
    text, _ = folder_c.convert(FolderContent(file_key="fk_1", file_name="docs"))
    assert text == '<folder key="fk_1" name="docs"/>'


def test_folder_with_key_only():
    text, _ = folder_c.convert(FolderContent(file_key="fk_1"))
    assert text == '<folder key="fk_1"/>'


def test_folder_no_key_falls_back_to_placeholder():
    text, _ = folder_c.convert(FolderContent(file_name="docs"))
    assert text == "[folder]"


# ---- merge_forward: header not indented, body indented 4 spaces -------------


def test_merge_forward_item_header_is_flush_left():
    child = MergeForwardItem(
        message_id="om_1",
        sender_name="Alice",
        create_time=1700000000000,
        content=TextContent(text="hello"),
    )
    mf = MergeForwardContent(items=[child])
    text, _ = mf_c.convert(mf)
    lines = text.split("\n")
    # Header line: "[timestamp] Alice:" — no leading spaces
    header_line = next(line for line in lines if "Alice:" in line)
    assert not header_line.startswith(" "), f"header should be flush-left: {header_line!r}"
    # Body line: "    hello" — 4 spaces
    body_line = next(line for line in lines if "hello" in line)
    assert body_line == "    hello", f"body should be indented 4 spaces: {body_line!r}"


def test_merge_forward_empty_or_loading_is_self_closing():
    assert mf_c.convert(MergeForwardContent(loading=True))[0] == "<forwarded_messages/>"
    assert mf_c.convert(MergeForwardContent(items=[]))[0] == "<forwarded_messages/>"


def test_merge_forward_nested_indents_by_4_more():
    inner_child = MergeForwardItem(
        message_id="om_inner",
        sender_name="Bob",
        create_time=1700000000000,
        content=TextContent(text="inner text"),
    )
    inner = MergeForwardContent(items=[inner_child])
    outer_child = MergeForwardItem(
        message_id="om_outer",
        sender_name="Alice",
        create_time=1700000000000,
        content=inner,
    )
    outer = MergeForwardContent(items=[outer_child])
    text, _ = mf_c.convert(outer)
    # The inner "inner text" line should be indented 8 spaces (4 from outer
    # body indent + 4 from inner body indent).
    inner_line = next(line for line in text.split("\n") if "inner text" in line)
    assert inner_line == "        inner text", f"nested body needs 8-space indent: {inner_line!r}"


def test_merge_forward_truncation_footer():
    child = MergeForwardItem(
        message_id="om_1",
        sender_name="Alice",
        create_time=1700000000000,
        content=TextContent(text="hi"),
    )
    mf = MergeForwardContent(items=[child], truncated=True)
    text, _ = mf_c.convert(mf)
    assert "... (truncated)" in text
    # Truncation marker should NOT be indented (node emits `\n... (truncated)`).
    assert "\n... (truncated)" in text


def test_merge_forward_missing_create_time_falls_back_to_unknown():
    child = MergeForwardItem(
        message_id="om_1",
        sender_name="Alice",
        create_time=None,
        content=TextContent(text="hi"),
    )
    mf = MergeForwardContent(items=[child])
    text, _ = mf_c.convert(mf)
    # Matches node's `timestamp = createMs > 0 ? format(...) : 'unknown'`.
    assert "[unknown] Alice:" in text


def test_merge_forward_item_that_raises_is_skipped():
    class _Boom:
        def __getattribute__(self, name):
            raise RuntimeError("simulated failure")

    ok_child = MergeForwardItem(
        message_id="om_1",
        sender_name="Alice",
        create_time=1700000000000,
        content=TextContent(text="good"),
    )
    mf = MergeForwardContent(items=[_Boom(), ok_child])
    text, _ = mf_c.convert(mf)
    # The good item survives; the broken one is silently dropped.
    assert "Alice:" in text
    assert "good" in text


# ---- Calendar edge cases -----------------------------------------------


def test_calendar_only_summary_no_time():
    text, _ = calendar_c.convert(CalendarContent(summary="Just a note"))
    assert "📅 Just a note" in text
    assert "🕙" not in text  # no time line when start/end absent


def test_calendar_only_start_no_end():
    text, _ = calendar_c.convert(CalendarContent(summary="S", start_time=1700000000000))
    assert "🕙 " in text
    assert "~" not in text  # no range separator when end missing


def test_calendar_empty_falls_back_to_placeholder():
    text, _ = calendar_c.convert(CalendarContent())
    assert text == "<calendar_invite>\n[calendar event]\n</calendar_invite>"


# ---- Vote edge cases ---------------------------------------------------


def test_vote_options_only_no_topic():
    text, _ = vote_c.convert(VoteContent(options=["A", "B"]))
    lines = text.split("\n")
    assert lines[0] == "<vote>"
    assert "• A" in lines and "• B" in lines
    assert lines[-1] == "</vote>"


# ---- Todo edge cases ---------------------------------------------------


def test_todo_only_due_time():
    text, _ = todo_c.convert(TodoContent(due_time=1700000000000))
    assert "Due: " in text


def test_todo_only_title():
    text, _ = todo_c.convert(TodoContent(title="finish audit"))
    assert "finish audit" in text
    assert "Due:" not in text


# ---- Share fallback for empty id --------------------------------------


def test_share_chat_with_empty_chat_id():
    # Node emits id="" for missing chat_id (``?? ''`` coalesce).
    text, _ = share_c.convert_chat(ShareChatContent(chat_id=""))
    assert text == '<group_card id=""/>'


# ---- System fallback --------------------------------------------------


def test_system_empty_raw_uses_template_as_is():
    # Template with no raw → variables can't resolve but template remains.
    content = SystemContent(template="Hello World")
    text, _ = system_c.convert(content)
    assert text == "Hello World"
