"""Property aliases on `InboundMessage`.

Verifies that `msg.message_id` / `msg.chat_id` / `msg.sender_id` /
`msg.chat_type` / `msg.reply_to_message_id` all project the expected values
from the underlying dataclasses.
"""

from lark_oapi.channel.types import (
    Conversation,
    Identity,
    InboundMessage,
    ReplyRef,
    ResourceDescriptor,
    ResourceType,
)


def test_message_id_property_aliases_id():
    msg = InboundMessage(
        id="om_abc", create_time=0,
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_1"),
    )
    assert msg.message_id == "om_abc"


def test_chat_id_and_chat_type_properties():
    msg = InboundMessage(
        id="om", create_time=0,
        conversation=Conversation(chat_id="oc_X", chat_type="group"),
        sender=Identity(open_id="ou_1"),
    )
    assert msg.chat_id == "oc_X"
    assert msg.chat_type == "group"


def test_sender_id_and_sender_name():
    msg = InboundMessage(
        id="om", create_time=0,
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_s", display_name="Alice"),
    )
    assert msg.sender_id == "ou_s"
    assert msg.sender_name == "Alice"


def test_reply_to_message_id_none_when_no_reply():
    msg = InboundMessage(
        id="om", create_time=0,
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_1"),
    )
    assert msg.reply_to_message_id is None


def test_reply_to_message_id_populated_from_reply():
    msg = InboundMessage(
        id="om", create_time=0,
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_1"),
        reply=ReplyRef(message_id="om_parent"),
    )
    assert msg.reply_to_message_id == "om_parent"


def test_default_content_text_and_resources_empty():
    msg = InboundMessage(
        id="om", create_time=0,
        conversation=Conversation(chat_id="oc_1", chat_type="p2p"),
        sender=Identity(open_id="ou_1"),
    )
    assert msg.content_text == ""
    assert msg.resources == []
    assert msg.mentioned_bot is False


def test_resource_descriptor_fields():
    r = ResourceDescriptor(
        type="video",
        file_key="v_x",
        file_name="clip.mp4",
        duration_ms=1500,
        cover_image_key="img_cover",
    )
    assert r.type == "video"
    assert r.duration_ms == 1500


def test_resource_type_values_match_node_spec():
    # The canonical Node-spec set of resource types
    assert set(ResourceType.__args__) == {"image", "file", "audio", "video", "sticker"}


def test_inbound_message_batched_sources_default_none():
    from lark_oapi.channel import InboundMessage, Conversation, Identity, TextContent
    m = InboundMessage(
        id="m1",
        create_time=0,
        conversation=Conversation(chat_id="c1", chat_type="p2p"),
        sender=Identity(open_id="ou_x"),
        content=TextContent(text="hi"),
    )
    assert m.batched_sources is None
