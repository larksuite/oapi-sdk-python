"""UAT device-flow runner — extracted from :class:`FeishuChannel`.

Performs the "check cache → refresh if needed → start device flow → prompt
user → poll until authorized" dance. Separated so :mod:`..channel` can stay
focused on lifecycle.
"""

import asyncio
from typing import Any, Dict, List

from lark_oapi.core.log import logger

from ..card.builder import new_card as _card_factory
from ..errors import UATAuthError
from ..types import UAT
from .device_flow import DeviceFlowClient, uat_needs_refresh
from .token_store import TokenStore

# Per-user-open-id asyncio locks so concurrent handler invocations for the
# same user don't both try to refresh an expiring token simultaneously. The
# interactive device-flow prompt/poll step runs outside this lock so a waiting
# authorization does not block unrelated cache reads forever.
# The locks bind to the loop of the first caller; callers on other loops fall
# back to lock-less behaviour (rare; same-user concurrency across loops is not
# a supported configuration).
_user_locks: Dict[str, asyncio.Lock] = {}


def _get_user_lock(user_open_id: str) -> asyncio.Lock:
    """Lazily create + memoize a per-user asyncio.Lock on the current loop."""
    return _user_locks.setdefault(user_open_id, asyncio.Lock())


async def require_user_auth(
        *,
        device_flow: DeviceFlowClient,
        token_store: TokenStore,
        uat_config: Any,
        user_open_id: str,
        scopes: List[str],
        context: Any,
) -> UAT:
    """Resolve a usable UAT for ``user_open_id``, running device flow if needed.

    ``uat_config`` is a :class:`~..config.UATConfig` with scope allow/block
    lists and the refresh slack; ``context`` is the object used to prompt the
    user and should expose ``respond(card)``.

    A per-user asyncio.Lock serializes concurrent callers for the same user
    through cache lookup and refresh. The prompt/poll device-flow phase is
    intentionally outside that lock.
    """
    ub = uat_config
    if ub.allowed_scopes is not None:
        for s in scopes:
            if s not in ub.allowed_scopes:
                raise UATAuthError(f"scope {s} not in allowed_scopes")
    if ub.blocked_scopes:
        for s in scopes:
            if s in ub.blocked_scopes:
                raise UATAuthError(f"scope {s} is blocked")

    async with _get_user_lock(user_open_id or ""):
        existing = await token_store.get(user_open_id or "")
        if existing is not None:
            missing = [s for s in scopes if s and s not in (existing.scopes or [])]
            if not missing:
                if uat_needs_refresh(
                        existing, slack_seconds=ub.refresh_before_expiry_seconds
                ):
                    if existing.refresh_token:
                        try:
                            refreshed = await device_flow.refresh(existing.refresh_token)
                            refreshed.open_id = user_open_id
                            if not refreshed.scopes and existing.scopes:
                                refreshed.scopes = existing.scopes
                            await token_store.set(user_open_id, refreshed)
                            return refreshed
                        except UATAuthError:
                            await token_store.delete(user_open_id)
                    else:
                        await token_store.delete(user_open_id)
                else:
                    return existing

        init = await device_flow.start(scopes)
    try:
        prompt_card = (
            _card_factory()
            .header(title="Authorization required", template="blue")
            .markdown(
                f"Please click the link to complete authorization: "
                f"{init.verification_uri_complete}\n\n"
                f"User code: `{init.user_code}`\n"
                f"Expires in: {init.expires_in}s"
            )
            .build()
        )
        if context is not None and hasattr(context, "respond"):
            await context.respond(prompt_card)
    except Exception as e:
        logger.warning("require_user_auth: failed to send prompt card: %s", e)

    uat = await device_flow.poll(
        init.device_code,
        interval=init.interval or ub.device_poll_interval_seconds,
        timeout_seconds=init.expires_in,
    )
    uat.open_id = user_open_id
    if not uat.scopes:
        uat.scopes = list(scopes)
    await token_store.set(user_open_id, uat)
    return uat
