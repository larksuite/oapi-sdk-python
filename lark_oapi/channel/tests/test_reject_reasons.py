"""Reject-reason vocabulary lock-in.

Pins the policy_* prefixed names so downstream
consumers (Hermes metrics) can match on a stable taxonomy.
"""

from typing import get_args

from lark_oapi.channel import RejectReason

EXPECTED_REASONS = {
    # Non-policy
    "stale",
    "duplicate",
    "lock_contention",
    "self_sent",
    # Policy
    "policy_dm_disabled",
    "policy_group_disabled",
    "policy_dm_not_in_allowlist",
    "policy_group_not_in_allowlist",
    "policy_blocklist",
    "policy_admin_only",
    "policy_no_mention",
    "policy_mention_all_blocked",
    "policy_sender_not_allowed",
}


def test_reject_reason_literal_exact_set():
    """RejectReason Literal must contain exactly the agreed-upon vocabulary."""
    actual = set(get_args(RejectReason))
    assert actual == EXPECTED_REASONS, (
        f"missing: {EXPECTED_REASONS - actual}, extra: {actual - EXPECTED_REASONS}"
    )


def test_legacy_reasons_removed():
    """Legacy unprefixed names must not appear — the rename is a clean cut."""
    legacy = {
        "group_not_allowed",
        "sender_not_allowed",
        "no_mention",
        "dm_disabled",
        "mention_all_blocked",
    }
    actual = set(get_args(RejectReason))
    overlap = actual & legacy
    assert not overlap, f"legacy reasons still present: {overlap}"


# --- PolicyConfig / GroupOverride schema ----------------------------------

from lark_oapi.channel import DmPolicy, GroupOverride, GroupPolicy, PolicyConfig


def test_group_policy_literal_includes_blocklist_and_admin_only():
    actual = set(get_args(GroupPolicy))
    assert actual == {"open", "allowlist", "blocklist", "admin_only", "disabled"}


def test_dm_policy_literal_includes_blocklist():
    actual = set(get_args(DmPolicy))
    assert actual == {"open", "allowlist", "blocklist", "disabled"}


def test_policy_config_has_new_fields_with_defaults():
    cfg = PolicyConfig()
    assert cfg.deny_from is None
    assert cfg.group_blocklist is None
    assert cfg.admins is None


def test_group_override_has_allowlist_and_blocklist():
    ov = GroupOverride()
    assert ov.allowlist is None
    assert ov.blocklist is None
