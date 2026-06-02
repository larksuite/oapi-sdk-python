"""Event-name constants and :data:`ChannelEventName` Literal type.

``FeishuChannel.on(name, handler)`` accepts any of the strings in
:data:`ChannelEventName`. Passing an unknown name is not a hard error — it
logs a warning at runtime — so typos like ``channel.on("messageReceive", ...)``
(the correct name is ``"message"``) will otherwise fail silently.

Two ways to guard against that:

1. **Use the constants** (``Events.MESSAGE``)::

        channel.on(Events.MESSAGE, handler)

2. **Type-check with** :data:`ChannelEventName`::

        from lark_oapi.channel import ChannelEventName

        event: ChannelEventName = "message"  # mypy/pyright catches typos
        channel.on(event, handler)

   ``FeishuChannel.on``'s type hint uses this Literal alias, so any type
   checker will flag unknown event names in callers.
"""

from typing import Literal

#: All event names accepted by :meth:`FeishuChannel.on`. The alias table in
#: :mod:`._coerce` normalizes snake_case aliases (``"bot_added"``, ``"card_action"``,
#: etc.) onto these canonical forms.
ChannelEventName = Literal[
    "message",
    "cardAction",
    "reaction",
    "botAdded",
    "botLeave",
    "messageRead",
    "reject",
    "comment",
    "raw",
    "reconnecting",
    "reconnected",
    "error",
]


class Events:
    """String constants for :meth:`FeishuChannel.on` event names.

    Prefer these over string literals so typos surface as ``AttributeError``
    at import time instead of a runtime no-op::

        channel.on(Events.MESSAGE, on_message)
        channel.on(Events.CARD_ACTION, on_card_action)
    """

    MESSAGE = "message"
    CARD_ACTION = "cardAction"
    REACTION = "reaction"
    BOT_ADDED = "botAdded"
    BOT_LEAVE = "botLeave"
    MESSAGE_READ = "messageRead"
    REJECT = "reject"
    COMMENT = "comment"
    RAW = "raw"
    RECONNECTING = "reconnecting"
    RECONNECTED = "reconnected"
    ERROR = "error"


__all__ = ["ChannelEventName", "Events"]
