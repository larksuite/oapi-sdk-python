"""Declarative policy judgement with run-time updatability.

Decision order:

Group chat:
    1. ``group_policy`` / per-chat override gates the chat or sender.
    2. ``require_mention`` checks bot mention or optionally ``@all``.
    3. ``respond_to_mention_all=False`` blocks standalone ``@all`` mentions.

DM:
    - ``dm_policy``: open / allowlist / blocklist / disabled
    - ``allow_from`` / ``deny_from`` match configured sender identity fields

Returns `(allowed: bool, reason?: RejectReason)`.
"""

import threading
from dataclasses import dataclass
from typing import List, Optional, Set

from ..config import PolicyConfig
from ..types import Identity, InboundMessage
from .types import RejectReason

_VALID_SENDER_IDENTITY_FIELDS = {"open_id", "user_id", "union_id"}


def _sender_identity_values(sender: Identity, fields: List[str]) -> Set[str]:
    values: Set[str] = set()
    for field in fields or ["open_id"]:
        if field not in _VALID_SENDER_IDENTITY_FIELDS:
            raise ValueError(f"invalid sender identity field: {field}")
        value = str(getattr(sender, field, "") or "")
        if value:
            values.add(value)
    return values


def _matches_any_sender_identity(sender_ids: Set[str], candidates) -> bool:
    return bool(sender_ids and candidates and sender_ids.intersection(set(candidates)))


@dataclass
class PolicyDecision:
    allowed: bool
    reason: Optional[RejectReason] = None


class PolicyGate:
    def __init__(self, policy: Optional[PolicyConfig] = None) -> None:
        self._policy = policy or PolicyConfig()
        self._bot_open_id: Optional[str] = None
        self._lock = threading.Lock()

    def set_bot_open_id(self, open_id: Optional[str]) -> None:
        with self._lock:
            self._bot_open_id = open_id

    def get_policy(self) -> PolicyConfig:
        with self._lock:
            return self._policy

    def update_policy(self, **changes) -> None:
        """Run-time partial update. Unknown keys are ignored."""
        with self._lock:
            for k, v in changes.items():
                if hasattr(self._policy, k):
                    setattr(self._policy, k, v)

    def evaluate(self, msg: InboundMessage) -> PolicyDecision:
        with self._lock:
            policy = self._policy
            bot_open_id = self._bot_open_id

        sender_ids = _sender_identity_values(msg.sender, policy.sender_identity_fields)

        # 1. admin bypass — always allowed regardless of any other gate
        if policy.admins and _matches_any_sender_identity(sender_ids, policy.admins):
            return PolicyDecision(True)

        chat_type = msg.conversation.chat_type
        if chat_type in ("group", "topic"):
            return self._evaluate_group(msg, policy, bot_open_id, sender_ids)
        return self._evaluate_dm(msg, policy, sender_ids)

    def _evaluate_group(
            self,
            msg: InboundMessage,
            policy: PolicyConfig,
            bot_open_id: Optional[str],
            sender_ids: Set[str],
    ) -> PolicyDecision:
        override = (policy.group_overrides or {}).get(msg.conversation.chat_id)

        # explicit per-override disable
        if override and override.enabled is False:
            return PolicyDecision(False, "policy_group_disabled")

        policy_kind = override.policy if override and override.policy else policy.group_policy

        if policy_kind == "disabled":
            return PolicyDecision(False, "policy_group_disabled")

        if policy_kind == "blocklist":
            # Per-override blocklist gates the chat's sender identities.
            # Global group_blocklist gates chat_ids.
            if override and override.blocklist is not None:
                if _matches_any_sender_identity(sender_ids, override.blocklist):
                    return PolicyDecision(False, "policy_blocklist")
            elif policy.group_blocklist and msg.conversation.chat_id in policy.group_blocklist:
                return PolicyDecision(False, "policy_blocklist")
            # Otherwise fall through — blocklist mode permits everyone not listed.

        elif policy_kind == "admin_only":
            if not policy.admins or not _matches_any_sender_identity(sender_ids, policy.admins):
                return PolicyDecision(False, "policy_admin_only")
            # Admins fall through to require_mention; an admin who forgot to
            # @-mention the bot in a group still hits the mention gate.

        elif policy_kind == "allowlist":
            # Per-override allowlist gates the chat's sender identities.
            # Global group_allowlist gates chat_ids.
            if override and override.allowlist is not None:
                if not _matches_any_sender_identity(sender_ids, override.allowlist):
                    return PolicyDecision(False, "policy_group_not_in_allowlist")
            else:
                if not policy.group_allowlist or msg.conversation.chat_id not in policy.group_allowlist:
                    return PolicyDecision(False, "policy_group_not_in_allowlist")

        # require_mention / mention_all (unchanged)
        require_mention = (
            override.require_mention
            if override and override.require_mention is not None
            else policy.require_mention
        )
        respond_mention_all = (
            override.respond_to_mention_all
            if override and override.respond_to_mention_all is not None
            else policy.respond_to_mention_all
        )
        mentioned_bot = bool(
            bot_open_id and any(m.open_id == bot_open_id for m in msg.mentions)
        )
        if require_mention:
            if not mentioned_bot and not (respond_mention_all and msg.mentioned_all):
                return PolicyDecision(False, "policy_no_mention")

        if msg.mentioned_all and not respond_mention_all and not mentioned_bot:
            return PolicyDecision(False, "policy_mention_all_blocked")

        if policy.allow_from and not _matches_any_sender_identity(sender_ids, policy.allow_from):
            return PolicyDecision(False, "policy_sender_not_allowed")

        return PolicyDecision(True)

    def _evaluate_dm(
            self, msg: InboundMessage, policy: PolicyConfig, sender_ids: Set[str]
    ) -> PolicyDecision:
        if policy.dm_policy == "disabled":
            return PolicyDecision(False, "policy_dm_disabled")
        if policy.dm_policy == "blocklist":
            if policy.deny_from and _matches_any_sender_identity(sender_ids, policy.deny_from):
                return PolicyDecision(False, "policy_blocklist")
            return PolicyDecision(True)
        if policy.dm_policy == "allowlist":
            if not policy.allow_from or not _matches_any_sender_identity(sender_ids, policy.allow_from):
                return PolicyDecision(False, "policy_dm_not_in_allowlist")
        return PolicyDecision(True)
