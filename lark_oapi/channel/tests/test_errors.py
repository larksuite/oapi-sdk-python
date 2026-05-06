"""Error classification tests."""

from lark_oapi.channel.errors import FeishuChannelErrorCode, classify_error


def test_token_invalid_is_retryable():
    e = classify_error(99991663, "expired")
    assert e.code == FeishuChannelErrorCode.PERMISSION_DENIED
    assert e.retryable is True


def test_rate_limit():
    assert classify_error(11020).code == FeishuChannelErrorCode.RATE_LIMITED


def test_target_revoked():
    assert classify_error(230002).code == FeishuChannelErrorCode.TARGET_REVOKED


def test_length_exceed_maps_to_format_error():
    e = classify_error(230021)
    assert e.code == FeishuChannelErrorCode.FORMAT_ERROR
    assert e.retryable is False


def test_5xx_maps_to_unknown_retryable():
    assert classify_error(500).code == FeishuChannelErrorCode.UNKNOWN
    assert classify_error(500).retryable is True
    assert classify_error(50100).code == FeishuChannelErrorCode.UNKNOWN


def test_unknown_defaults():
    e = classify_error(123456)
    assert e.code == FeishuChannelErrorCode.UNKNOWN
    assert e.retryable is False


def test_zero_is_unknown_and_non_retryable():
    assert classify_error(0).retryable is False


def test_download_failed_enum_value_exists():
    from lark_oapi.channel import FeishuChannelErrorCode
    assert FeishuChannelErrorCode.DOWNLOAD_FAILED.value == "download_failed"
