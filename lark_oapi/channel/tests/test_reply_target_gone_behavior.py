import pytest

from lark_oapi.channel import OutboundSender, OutboundText
from lark_oapi.channel._coerce import coerce_send_opts
from lark_oapi.channel.config import OutboundConfig, RetryConfig
from lark_oapi.channel.errors import FeishuChannelErrorCode


class RecordingDriver:
    def __init__(self, reply_raw=None):
        self.reply_raw = reply_raw or {"code": 0, "data": {"message_id": "om_reply"}}
        self.create_calls = []
        self.reply_calls = []

    async def reply_message(self, **kwargs):
        self.reply_calls.append(kwargs)
        return self.reply_raw

    async def create_message(self, **kwargs):
        self.create_calls.append(kwargs)
        return {"code": 0, "data": {"message_id": "om_create"}}


def _sender(driver):
    return OutboundSender(
        driver,
        config=OutboundConfig(retry=RetryConfig(max_attempts=1, base_delay_ms=0)),
    )


def test_coerce_send_opts_defaults_reply_target_gone_to_fresh():
    opts = coerce_send_opts(None)

    assert opts.reply_target_gone == "fresh"


def test_coerce_send_opts_accepts_snake_case_reply_target_gone():
    opts = coerce_send_opts({"reply_target_gone": "fail"})

    assert opts.reply_target_gone == "fail"


def test_coerce_send_opts_accepts_camel_case_reply_target_gone():
    opts = coerce_send_opts({"replyTargetGone": "fail"})

    assert opts.reply_target_gone == "fail"


def test_coerce_send_opts_rejects_invalid_reply_target_gone():
    with pytest.raises(ValueError, match="invalid reply_target_gone: ignore"):
        coerce_send_opts({"reply_target_gone": "ignore"})


@pytest.mark.asyncio
async def test_reply_target_gone_defaults_to_fresh_create():
    driver = RecordingDriver(reply_raw={"code": 230002, "msg": "target gone"})

    result = await _sender(driver).send(
        OutboundText(text="hello"),
        receive_id="oc_chat",
        receive_id_type="chat_id",
        reply_to="om_parent",
    )

    assert result.success is True
    assert result.message_id == "om_create"
    assert len(driver.reply_calls) == 1
    assert len(driver.create_calls) == 1


@pytest.mark.asyncio
async def test_reply_target_gone_fail_returns_reply_failure_without_create():
    driver = RecordingDriver(reply_raw={"code": 230002, "msg": "target gone"})

    result = await _sender(driver).send(
        OutboundText(text="hello"),
        receive_id="oc_chat",
        receive_id_type="chat_id",
        reply_to="om_parent",
        reply_target_gone="fail",
    )

    assert result.success is False
    assert result.error.code == FeishuChannelErrorCode.TARGET_REVOKED
    assert len(driver.reply_calls) == 1
    assert len(driver.create_calls) == 0


@pytest.mark.asyncio
async def test_reply_in_thread_still_passes_to_reply_request():
    driver = RecordingDriver()

    result = await _sender(driver).send(
        OutboundText(text="hello"),
        receive_id="oc_chat",
        receive_id_type="chat_id",
        reply_to="om_parent",
        reply_in_thread=True,
        reply_target_gone="fail",
    )

    assert result.success is True
    assert driver.reply_calls[0]["reply_in_thread"] is True


@pytest.mark.asyncio
async def test_multi_chunk_reply_target_gone_fail_stops_after_first_chunk():
    driver = RecordingDriver(reply_raw={"code": 230002, "msg": "target gone"})
    sender = _sender(driver)
    sender._config.text_chunk_limit = 5

    result = await sender.send(
        OutboundText(text="first\nsecond\nthird"),
        receive_id="oc_chat",
        receive_id_type="chat_id",
        reply_to="om_parent",
        reply_target_gone="fail",
    )

    assert result.success is False
    assert result.error.code == FeishuChannelErrorCode.TARGET_REVOKED
    assert len(driver.reply_calls) == 1
    assert len(driver.create_calls) == 0
