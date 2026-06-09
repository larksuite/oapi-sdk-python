"""Tests for rich policy behavior.

Covers admin bypass, blocklist (DM + group + per-override), admin_only,
and per-override allowlist precedence.
"""

from lark_oapi.channel import GroupOverride, PolicyConfig
from lark_oapi.channel.safety.policy_gate import PolicyGate
from lark_oapi.channel.types import (
    Conversation,
    Identity,
    InboundMessage,
    TextContent,
)

BOT = "ou_bot"
ADMIN = "ou_admin"
USER = "ou_user"
EVIL = "ou_evil"


def _msg(*, chat_type: str, chat_id: str, sender: str, mentions=None, mentioned_all=False, text="hi"):
    return InboundMessage(
        id="m1",
        create_time=0,
        conversation=Conversation(chat_id=chat_id, chat_type=chat_type),
        sender=Identity(open_id=sender),
        mentions=mentions or [],
        mentioned_all=mentioned_all,
        content=TextContent(text=text),
    )


# --- admin bypass ---------------------------------------------------------

def test_admin_bypasses_disabled_group():
    gate = PolicyGate(PolicyConfig(group_policy="disabled", admins=[ADMIN]))
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c1", sender=ADMIN))
    assert decision.allowed is True


def test_admin_bypasses_dm_disabled():
    gate = PolicyGate(PolicyConfig(dm_policy="disabled", admins=[ADMIN]))
    decision = gate.evaluate(_msg(chat_type="p2p", chat_id="c1", sender=ADMIN))
    assert decision.allowed is True


def test_non_admin_still_blocked_when_disabled():
    gate = PolicyGate(PolicyConfig(group_policy="disabled", admins=[ADMIN]))
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c1", sender=USER))
    assert decision.allowed is False
    assert decision.reason == "policy_group_disabled"


# --- DM blocklist ---------------------------------------------------------

def test_dm_blocklist_blocks_listed_sender():
    gate = PolicyGate(PolicyConfig(dm_policy="blocklist", deny_from=[EVIL]))
    decision = gate.evaluate(_msg(chat_type="p2p", chat_id="c1", sender=EVIL))
    assert decision.allowed is False
    assert decision.reason == "policy_blocklist"


def test_dm_blocklist_passes_unlisted_sender():
    gate = PolicyGate(PolicyConfig(dm_policy="blocklist", deny_from=[EVIL]))
    decision = gate.evaluate(_msg(chat_type="p2p", chat_id="c1", sender=USER))
    assert decision.allowed is True


# --- Group blocklist ------------------------------------------------------

def test_group_blocklist_blocks_listed_chat():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="blocklist",
            group_blocklist=["c_blocked"],
            require_mention=False,
        )
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c_blocked", sender=USER))
    assert decision.allowed is False
    assert decision.reason == "policy_blocklist"


def test_group_blocklist_passes_unlisted_chat():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="blocklist",
            group_blocklist=["c_blocked"],
            require_mention=False,
        )
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c_ok", sender=USER))
    assert decision.allowed is True


# --- admin_only ----------------------------------------------------------

def test_admin_only_passes_admin():
    gate = PolicyGate(
        PolicyConfig(group_policy="admin_only", admins=[ADMIN], require_mention=False)
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c1", sender=ADMIN))
    assert decision.allowed is True


def test_admin_only_blocks_non_admin():
    gate = PolicyGate(
        PolicyConfig(group_policy="admin_only", admins=[ADMIN], require_mention=False)
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c1", sender=USER))
    assert decision.allowed is False
    assert decision.reason == "policy_admin_only"


def test_admin_only_blocks_when_admins_unset():
    gate = PolicyGate(PolicyConfig(group_policy="admin_only", require_mention=False))
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c1", sender=USER))
    assert decision.allowed is False
    assert decision.reason == "policy_admin_only"


# --- per-override blocklist + allowlist ----------------------------------

def test_group_override_blocklist_takes_effect():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="open",
            group_overrides={
                "c_special": GroupOverride(policy="blocklist", blocklist=[EVIL])
            },
            require_mention=False,
        )
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c_special", sender=EVIL))
    assert decision.allowed is False
    assert decision.reason == "policy_blocklist"


def test_group_override_allowlist_takes_effect():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="open",
            group_overrides={
                "c_special": GroupOverride(policy="allowlist", allowlist=[USER])
            },
            require_mention=False,
        )
    )
    gate.set_bot_open_id(BOT)
    decision = gate.evaluate(_msg(chat_type="group", chat_id="c_special", sender=EVIL))
    assert decision.allowed is False
    assert decision.reason == "policy_group_not_in_allowlist"
