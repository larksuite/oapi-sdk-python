"""Tests for receive_id_type inference."""

from lark_oapi.channel.outbound.routing import infer_receive_id_type


def test_open_id():
    assert infer_receive_id_type("ou_abc") == "open_id"


def test_chat_id():
    assert infer_receive_id_type("oc_xyz") == "chat_id"


def test_union_id():
    assert infer_receive_id_type("on_foo") == "union_id"


def test_email():
    assert infer_receive_id_type("a@b.com") == "email"


def test_user_id_default():
    assert infer_receive_id_type("123456") == "user_id"


def test_empty_is_chat_id():
    assert infer_receive_id_type("") == "chat_id"
