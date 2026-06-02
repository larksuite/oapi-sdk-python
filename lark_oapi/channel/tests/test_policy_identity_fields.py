import pytest

from lark_oapi.channel import Conversation, GroupOverride, Identity, InboundMessage
from lark_oapi.channel.config import PolicyConfig
from lark_oapi.channel.safety.policy_gate import PolicyGate
from lark_oapi.channel.types import TextContent


def _message(
        *,
        chat_type="group",
        open_id="ou_alice",
        user_id="u_alice",
        union_id="on_alice",
        chat_id="oc_chat",
):
    return InboundMessage(
        id="om_1",
        create_time=1,
        conversation=Conversation(chat_id=chat_id, chat_type=chat_type),
        sender=Identity(open_id=open_id, user_id=user_id, union_id=union_id),
        content=TextContent(text="hello"),
    )


def test_policy_default_sender_identity_fields_only_match_open_id():
    gate = PolicyGate(PolicyConfig(allow_from=["u_alice"], require_mention=False))

    decision = gate.evaluate(_message())

    assert decision.allowed is False
    assert decision.reason == "policy_sender_not_allowed"


def test_policy_allow_from_matches_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            allow_from=["u_alice"],
            require_mention=False,
            sender_identity_fields=["open_id", "user_id"],
        )
    )

    decision = gate.evaluate(_message())

    assert decision.allowed is True


def test_policy_admin_only_matches_admin_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="admin_only",
            admins=["u_admin"],
            require_mention=False,
            sender_identity_fields=["open_id", "user_id"],
        )
    )

    decision = gate.evaluate(_message(user_id="u_admin"))

    assert decision.allowed is True


def test_policy_group_override_allowlist_matches_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="allowlist",
            require_mention=False,
            sender_identity_fields=["open_id", "user_id"],
            group_overrides={
                "oc_chat": GroupOverride(allowlist=["u_alice"]),
            },
        )
    )

    decision = gate.evaluate(_message())

    assert decision.allowed is True


def test_policy_group_override_blocklist_matches_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            group_policy="blocklist",
            require_mention=False,
            sender_identity_fields=["open_id", "user_id"],
            group_overrides={
                "oc_chat": GroupOverride(blocklist=["u_bad"]),
            },
        )
    )

    decision = gate.evaluate(_message(user_id="u_bad"))

    assert decision.allowed is False
    assert decision.reason == "policy_blocklist"


def test_policy_dm_allowlist_matches_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            dm_policy="allowlist",
            allow_from=["u_alice"],
            sender_identity_fields=["open_id", "user_id"],
        )
    )

    decision = gate.evaluate(_message(chat_type="p2p"))

    assert decision.allowed is True


def test_policy_dm_blocklist_matches_user_id_when_configured():
    gate = PolicyGate(
        PolicyConfig(
            dm_policy="blocklist",
            deny_from=["u_bad"],
            sender_identity_fields=["open_id", "user_id"],
        )
    )

    decision = gate.evaluate(_message(chat_type="p2p", user_id="u_bad"))

    assert decision.allowed is False
    assert decision.reason == "policy_blocklist"


def test_policy_invalid_sender_identity_field_raises():
    gate = PolicyGate(
        PolicyConfig(
            allow_from=["u_alice"],
            sender_identity_fields=["email"],
        )
    )

    with pytest.raises(ValueError, match="invalid sender identity field: email"):
        gate.evaluate(_message())
