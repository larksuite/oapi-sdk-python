"""Channel error types and classification.

Single canonical enum: `FeishuChannelErrorCode` — 10 values covering the
taxonomy of failures surfaced by the outbound / inbound pipelines.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class FeishuChannelErrorCode(str, Enum):
    """Channel-layer error taxonomy (10 canonical values)."""

    FORMAT_ERROR = "format_error"
    TARGET_REVOKED = "target_revoked"
    RATE_LIMITED = "rate_limited"
    PERMISSION_DENIED = "permission_denied"
    UPLOAD_FAILED = "upload_failed"
    DOWNLOAD_FAILED = "download_failed"
    SSRF_BLOCKED = "ssrf_blocked"
    SEND_TIMEOUT = "send_timeout"
    NOT_CONNECTED = "not_connected"
    UNKNOWN = "unknown"


@dataclass
class SendError:
    code: FeishuChannelErrorCode
    retryable: bool
    hint: Optional[str] = None
    raw_code: Optional[int] = None
    # Suggested minimum wait before retrying. Populated when the upstream
    # response carries a ``Retry-After`` header (seconds) or an equivalent
    # rate-limit hint. ``None`` means "use default backoff".
    retry_after_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "retryable": self.retryable,
            "hint": self.hint,
            "raw_code": self.raw_code,
            "retry_after_seconds": self.retry_after_seconds,
        }


# Feishu API error code buckets
_TOKEN_INVALID_CODES = {99991663, 99991664, 99991665, 99991666, 99991668}
# 99991402 / 11020 / 11021 are genuine "too many requests" backpressure codes;
# 99991400 / 99991401 used to be miscategorized here but are actually auth /
# permission denials ("invalid app_ticket" / "invalid access_token") so they
# live in _PERMISSION_CODES below.
_RATE_LIMIT_CODES = {99991402, 11020, 11021}
# 230001 = "invalid message content" (malformed body); NOT a revoked target.
# Do NOT put it in _TARGET_REVOKED_CODES — that triggers the wrong fallback
# (reply-gone → fresh create) and hides the real schema bug.
_TARGET_REVOKED_CODES = {230002, 230005, 230020, 230017}
_LENGTH_EXCEED_CODES = {230021, 230022}
_PERMISSION_CODES = {
    99991400, 99991401,  # auth/token denials (not rate-limit)
    99991672, 99991679, 99991680, 99991681,
    230003, 230010,
}
_FORMAT_CODES = {
    230001,  # invalid message content — shape mismatch, malformed JSON, etc.
    230099,  # CardKit "failed to create card content"
}


def classify_error(raw_code: int, msg: str = "") -> SendError:
    """Classify a Feishu API error code into a `SendError`."""
    if raw_code == 0:
        return SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=False, raw_code=0, hint=msg)
    if raw_code in _TOKEN_INVALID_CODES:
        return SendError(code=FeishuChannelErrorCode.PERMISSION_DENIED, retryable=True, raw_code=raw_code, hint=msg)
    if raw_code in _RATE_LIMIT_CODES:
        return SendError(code=FeishuChannelErrorCode.RATE_LIMITED, retryable=True, raw_code=raw_code, hint=msg)
    if raw_code in _TARGET_REVOKED_CODES:
        return SendError(code=FeishuChannelErrorCode.TARGET_REVOKED, retryable=False, raw_code=raw_code, hint=msg)
    if raw_code in _LENGTH_EXCEED_CODES:
        return SendError(code=FeishuChannelErrorCode.FORMAT_ERROR, retryable=False, raw_code=raw_code, hint=msg)
    if raw_code in _PERMISSION_CODES:
        return SendError(code=FeishuChannelErrorCode.PERMISSION_DENIED, retryable=False, raw_code=raw_code, hint=msg)
    if raw_code in _FORMAT_CODES:
        return SendError(code=FeishuChannelErrorCode.FORMAT_ERROR, retryable=False, raw_code=raw_code, hint=msg)
    if 500 <= raw_code < 600 or 50000 <= raw_code < 60000:
        return SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=True, raw_code=raw_code, hint=msg)
    return SendError(code=FeishuChannelErrorCode.UNKNOWN, retryable=False, raw_code=raw_code, hint=msg)


class _ChannelError(Exception):
    """Base class for channel-layer errors that escape user handlers.

    Kept as an internal inheritance root; user-facing code should catch
    :class:`FeishuChannelError`.
    """


class UATAuthError(_ChannelError):
    """UAT device-flow authorization failed or was cancelled."""


class PolicyDeniedError(_ChannelError):
    """Raised internally when a policy gate blocks a message."""


class FeishuChannelError(_ChannelError):
    """Unified channel error raised by the outbound / inbound pipelines.

    Prefer the ``raise FeishuChannelError(...) from original_exc`` idiom to
    preserve the underlying cause in tracebacks. The ``cause=`` kwarg below is
    kept for back-compat: when supplied it is wired to ``__cause__`` so
    ``traceback.print_exc()`` still shows the chain.
    """

    def __init__(
            self,
            code: FeishuChannelErrorCode,
            message: str = "",
            *,
            cause: Optional[BaseException] = None,
            context: Optional[Dict[str, Any]] = None,
    ) -> None:
        resolved = message or code.value
        super().__init__(resolved)
        self.code = code
        # Stored explicitly so ``__repr__`` / diagnostics don't depend on the
        # fragile ``self.args[0]`` indexing.
        self.message: str = resolved
        self.context = context or {}
        # Wire to Python's exception-chaining machinery so tracebacks show the
        # root cause. Previously this kwarg was stored but never surfaced.
        if cause is not None:
            self.__cause__ = cause

    @property
    def cause(self) -> Optional[BaseException]:
        """Back-compat shim: returns the wired ``__cause__``."""
        c = self.__cause__
        return c if isinstance(c, BaseException) else None

    def __repr__(self) -> str:
        return (
            f"FeishuChannelError(code={self.code.value}, "
            f"message={self.message!r})"
        )


class OutboundSendError(FeishuChannelError):
    """Exception form of :class:`SendError` — what ``on('error', ...)`` handlers
    actually receive when a send/stream call returns ``SendResult.fail(...)``.

    Subscribers consume errors uniformly (``logger.exception``,
    ``traceback.format_exception``, Sentry, etc.); these expect a real
    :class:`Exception` with ``__traceback__``. Forwarding a bare
    :class:`SendError` dataclass would break that contract. This wrapper
    preserves every field of the original ``SendError`` and is a subclass of
    :class:`FeishuChannelError`, so existing ``except FeishuChannelError``
    catches still work.

    The original ``SendResult.fail(...)`` returned to the direct caller is
    unchanged — wrapping happens only on the forwarding path.
    """

    def __init__(self, send_error: SendError) -> None:
        super().__init__(
            send_error.code,
            send_error.hint or send_error.code.value,
        )
        self.send_error = send_error
        self.retryable = send_error.retryable
        self.raw_code = send_error.raw_code
        self.retry_after_seconds = send_error.retry_after_seconds
        self.hint = send_error.hint

    def __repr__(self) -> str:
        return (
            f"OutboundSendError(code={self.code.value}, "
            f"raw_code={self.raw_code}, retryable={self.retryable}, "
            f"hint={self.hint!r})"
        )


# ---- Classification helpers -------------------------------------------------


def classify_api_error(raw_code: int, msg: str = "") -> FeishuChannelErrorCode:
    """Map a Feishu API error code to a :class:`FeishuChannelErrorCode`.

    Thin shim around :func:`classify_error` — use that directly when you need
    the full ``SendError`` (retryable flag, raw code, hint). Kept for callers
    that only care about the taxonomy code.
    """
    return classify_error(raw_code, msg).code


def classify_http_status(status: int) -> FeishuChannelErrorCode:
    """Map an HTTP status code to a ``FeishuChannelErrorCode``."""
    if status == 429:
        return FeishuChannelErrorCode.RATE_LIMITED
    if status in (401, 403):
        return FeishuChannelErrorCode.PERMISSION_DENIED
    if status == 404:
        return FeishuChannelErrorCode.TARGET_REVOKED
    if status == 400:
        return FeishuChannelErrorCode.FORMAT_ERROR
    return FeishuChannelErrorCode.UNKNOWN


def is_retryable(code: FeishuChannelErrorCode) -> bool:
    return code in (FeishuChannelErrorCode.RATE_LIMITED, FeishuChannelErrorCode.UNKNOWN)


def is_reply_target_gone(code: FeishuChannelErrorCode) -> bool:
    return code == FeishuChannelErrorCode.TARGET_REVOKED


def is_format_error(code: FeishuChannelErrorCode) -> bool:
    return code == FeishuChannelErrorCode.FORMAT_ERROR
