"""Drop messages that are too old to care about.

Motivation: after a WebSocket reconnect, Feishu replays recent events it
believes we missed. If our process just restarted, that means we'll receive
messages from before the crash — which the user already stopped expecting a
reply to. We silently drop events older than `window_ms` (default 30 min).
"""

import time

DEFAULT_STALE_MS = 30 * 60 * 1000


def is_stale(create_time_ms: int, window_ms: int = DEFAULT_STALE_MS) -> bool:
    """Return True if `create_time_ms` is older than `window_ms` ago."""
    if not create_time_ms:
        return False
    now_ms = int(time.time() * 1000)
    return (now_ms - create_time_ms) > window_ms
