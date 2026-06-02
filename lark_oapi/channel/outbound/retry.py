"""Exponential-backoff retry for transient outbound failures.

Defaults:
    - 3 attempts total (1 initial + 2 retries)
    - ``500ms * 3 ** attempt`` backoff (500ms, 1.5s, 4.5s ...), capped at
      ``DEFAULT_MAX_DELAY_MS`` to avoid multi-minute waits under repeated
      failure.

If the ``SendError`` carries a ``retry_after_seconds`` value (populated from
an upstream ``Retry-After`` header on 429s), that value overrides the
computed backoff — honouring server-signalled rate limits rather than
hammering with a smaller client-side delay. We still cap the absolute wait
to ``DEFAULT_MAX_RETRY_AFTER_S`` so a misbehaving server can't stall a
caller for minutes.

Only retries when the caller flags the last result as retryable; other
failures are returned immediately.
"""

import asyncio
import random
from typing import Awaitable, Callable, Optional

from ..errors import SendError, is_retryable
from ..types import SendResult

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY_MS = 500
DEFAULT_MAX_DELAY_MS = 30_000
DEFAULT_MAX_RETRY_AFTER_S = 60.0


async def with_retry(
        op: Callable[[int], Awaitable[SendResult]],
        *,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        base_delay_ms: int = DEFAULT_BASE_DELAY_MS,
        max_delay_ms: int = DEFAULT_MAX_DELAY_MS,
        jitter: bool = True,
) -> SendResult:
    """Call `op(attempt)` up to `max_attempts` times with backoff.

    `op` is expected to return a `SendResult`. If `result.success` is False
    and the error is retryable (see `errors.is_retryable`), we back off and
    try again; otherwise we short-circuit.
    """
    last: Optional[SendResult] = None
    for attempt in range(max_attempts):
        result = await op(attempt)
        if result.success:
            return result
        last = result
        if result.error is None or not _should_retry(result.error):
            return result
        # Not the last attempt → sleep then retry
        if attempt >= max_attempts - 1:
            return result
        delay = _compute_delay(
            result.error, attempt,
            base_delay_ms=base_delay_ms,
            max_delay_ms=max_delay_ms,
            jitter=jitter,
        )
        await asyncio.sleep(delay)
    if last is None:
        raise RuntimeError("with_retry: no attempt was made (max_attempts<=0?)")
    return last


def _compute_delay(
        err: SendError, attempt: int, *,
        base_delay_ms: int, max_delay_ms: int, jitter: bool,
) -> float:
    """Compute seconds to sleep before the next retry.

    Server-signalled ``retry_after_seconds`` wins when present; otherwise
    fall back to exponential backoff with optional jitter, capped at
    ``max_delay_ms``.
    """
    if err.retry_after_seconds is not None and err.retry_after_seconds > 0:
        # Bound to a sane ceiling so a broken upstream can't stall the
        # caller for multi-minute waits.
        return min(float(err.retry_after_seconds), DEFAULT_MAX_RETRY_AFTER_S)
    delay_ms = min(base_delay_ms * (3 ** attempt), max_delay_ms)
    delay = delay_ms / 1000.0
    if jitter:
        delay *= 0.7 + 0.6 * random.random()
    return delay


def _should_retry(err: SendError) -> bool:
    # Honor both the `retryable` flag set by `classify_error` (legacy) and
    # the aligned error-code predicate.
    return bool(err.retryable or is_retryable(err.code))
