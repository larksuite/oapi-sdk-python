"""Coverage for safety/types.py default values."""

from lark_oapi.channel.safety.types import (
    BatchConfig,
    ChatQueueConfig,
    DedupConfig,
    MediaBatchConfig,
    RejectEvent,
    TextBatchConfig,
)


def test_text_batch_defaults_match_node_spec():
    t = TextBatchConfig()
    assert t.delay_ms == 600
    assert t.long_threshold_chars == 1000
    assert t.long_delay_ms == 2000
    assert t.max_messages == 8
    assert t.max_chars == 4000


def test_batch_config_composes_text_and_media():
    b = BatchConfig()
    assert isinstance(b.text, TextBatchConfig)
    assert isinstance(b.media, MediaBatchConfig)


# --- MediaBatchConfig schema ----------------------------------------------

from lark_oapi.channel import MediaBatchConfig as PublicMediaBatchConfig
from lark_oapi.channel import SafetyConfig


def test_media_batch_default_disabled():
    """Default must keep enabled=False so existing setups don't change behavior."""
    m = PublicMediaBatchConfig()
    assert m.enabled is False
    assert m.delay_ms == 800
    assert m.max_items == 9
    assert m.compatible_kinds == frozenset({"image", "file", "audio", "video"})


def test_safety_config_media_batch_default_present():
    cfg = SafetyConfig()
    assert isinstance(cfg.media_batch, PublicMediaBatchConfig)
    assert cfg.media_batch.enabled is False


def test_chat_queue_enabled_by_default():
    assert ChatQueueConfig().enabled is True


def test_dedup_config_defaults_match_12h_12h():
    d = DedupConfig()
    assert d.ttl_seconds == 12 * 3600
    assert d.max_entries == 5000
    assert d.sweep_seconds == 5 * 60


def test_reject_event_is_a_simple_dataclass():
    e = RejectEvent(
        message_id="om_1", chat_id="oc_1", sender_id="ou_1",
        reason="policy_dm_disabled",
    )
    assert e.reason == "policy_dm_disabled"
    assert e.message_id == "om_1"
