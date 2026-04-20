"""Converters: ShareChatContent / ShareUserContent → card placeholders.

Aligned with node-sdk's ``converters/share.ts``: both use ``id="..."`` as the
attribute (not ``chat_id`` / ``user_id``).
"""

from typing import List, Tuple

from ...types import ResourceDescriptor, ShareChatContent, ShareUserContent
from ._utils import attr


def convert_chat(content: ShareChatContent) -> Tuple[str, List[ResourceDescriptor]]:
    return f'<group_card id="{attr(content.chat_id)}"/>', []


def convert_user(content: ShareUserContent) -> Tuple[str, List[ResourceDescriptor]]:
    return f'<contact_card id="{attr(content.user_id)}"/>', []
