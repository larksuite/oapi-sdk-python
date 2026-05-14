"""Infer `receive_id_type` for Lark's `POST /im/v1/messages` endpoint.

Lark requires you to say whether `receive_id` is an open_id, chat_id, user_id,
union_id, or email. In channel use cases the id format is usually obvious from
the prefix, so we auto-detect.
"""

from typing import Literal

ReceiveIdType = Literal["open_id", "chat_id", "user_id", "union_id", "email"]


def infer_receive_id_type(receive_id: str) -> ReceiveIdType:
    if not receive_id:
        return "chat_id"
    if "@" in receive_id:
        return "email"
    if receive_id.startswith("ou_"):
        return "open_id"
    if receive_id.startswith("oc_"):
        return "chat_id"
    if receive_id.startswith("on_"):
        return "union_id"
    # Anything else is likely a user_id or custom identifier.
    return "user_id"
