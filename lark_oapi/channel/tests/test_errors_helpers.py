"""Coverage for classify_api_error / classify_http_status / is_retryable /
is_reply_target_gone / is_format_error / FeishuChannelError."""

from lark_oapi.channel.errors import (
    FeishuChannelError,
    FeishuChannelErrorCode,
    classify_api_error,
    classify_http_status,
    is_format_error,
    is_reply_target_gone,
    is_retryable,
)


def test_feishu_channel_error_code_has_10_canonical_values():
    canonical = {
        "format_error", "target_revoked", "rate_limited", "permission_denied",
        "upload_failed", "download_failed", "ssrf_blocked", "send_timeout",
        "not_connected", "unknown",
    }
    assert {m.value for m in FeishuChannelErrorCode} == canonical


def test_feishu_channel_error_construction():
    err = FeishuChannelError(FeishuChannelErrorCode.FORMAT_ERROR, "bad card", context={"to": "oc_x"})
    assert err.code == FeishuChannelErrorCode.FORMAT_ERROR
    assert err.context == {"to": "oc_x"}
    assert "format_error" in repr(err) or "bad card" in repr(err)


def test_feishu_channel_error_default_message_uses_code():
    err = FeishuChannelError(FeishuChannelErrorCode.NOT_CONNECTED)
    assert err.args[0] == "not_connected"


def test_classify_api_error_target_revoked_family():
    # 230001 is NOT target_revoked — it is "invalid message content" (format error).
    # Regression: putting 230001 in the target_revoked bucket triggered the
    # reply-gone → fresh-create fallback, hiding schema bugs until prod.
    for code in (230020, 230017, 230002, 230005):
        assert classify_api_error(code) == FeishuChannelErrorCode.TARGET_REVOKED, code


def test_classify_api_error_230001_is_format_error_not_target_revoked():
    # See Feishu error-code docs: 230001 "invalid message content" =
    # malformed body / schema violation. Must route through the plain-text
    # fallback path (is_format_error), not the reply-gone path.
    from lark_oapi.channel.errors import classify_error, is_format_error

    assert classify_api_error(230001) == FeishuChannelErrorCode.FORMAT_ERROR
    err = classify_error(230001, "invalid message content")
    assert is_format_error(err.code)


def test_classify_api_error_permission_denied_family():
    for code in (99991400, 99991401, 99991672, 99991679, 99991680, 99991681, 230003, 230010):
        assert classify_api_error(code) == FeishuChannelErrorCode.PERMISSION_DENIED, code


def test_classify_api_error_rate_limited_family():
    for code in (99991402, 11020, 11021):
        assert classify_api_error(code) == FeishuChannelErrorCode.RATE_LIMITED, code


def test_classify_api_error_format_family():
    for code in (230099, 230021, 230022):
        assert classify_api_error(code) == FeishuChannelErrorCode.FORMAT_ERROR, code


def test_classify_api_error_unknown_fallback():
    assert classify_api_error(123456) == FeishuChannelErrorCode.UNKNOWN


def test_classify_api_error_zero_is_unknown():
    assert classify_api_error(0) == FeishuChannelErrorCode.UNKNOWN


def test_classify_http_status_mapping():
    assert classify_http_status(429) == FeishuChannelErrorCode.RATE_LIMITED
    assert classify_http_status(401) == FeishuChannelErrorCode.PERMISSION_DENIED
    assert classify_http_status(403) == FeishuChannelErrorCode.PERMISSION_DENIED
    assert classify_http_status(404) == FeishuChannelErrorCode.TARGET_REVOKED
    assert classify_http_status(400) == FeishuChannelErrorCode.FORMAT_ERROR
    assert classify_http_status(503) == FeishuChannelErrorCode.UNKNOWN
    assert classify_http_status(200) == FeishuChannelErrorCode.UNKNOWN


def test_is_retryable_predicate():
    assert is_retryable(FeishuChannelErrorCode.RATE_LIMITED) is True
    assert is_retryable(FeishuChannelErrorCode.UNKNOWN) is True
    assert is_retryable(FeishuChannelErrorCode.FORMAT_ERROR) is False
    assert is_retryable(FeishuChannelErrorCode.TARGET_REVOKED) is False
    assert is_retryable(FeishuChannelErrorCode.PERMISSION_DENIED) is False


def test_is_reply_target_gone_predicate():
    assert is_reply_target_gone(FeishuChannelErrorCode.TARGET_REVOKED) is True
    assert is_reply_target_gone(FeishuChannelErrorCode.FORMAT_ERROR) is False


def test_is_format_error_predicate():
    assert is_format_error(FeishuChannelErrorCode.FORMAT_ERROR) is True
    assert is_format_error(FeishuChannelErrorCode.UNKNOWN) is False
