"""Coverage for the config dataclasses — default values + nesting."""

from lark_oapi.channel.config import (
    ChannelConfig,
    DedupConfig,
    FooterConfig,
    GroupOverride,
    InboundConfig,
    MarkdownConverter,
    MediaCapabilities,
    NameCacheConfig,
    OutboundConfig,
    PerChatReplyMode,
    PolicyConfig,
    RetryConfig,
    SafetyConfig,
    StreamThrottleConfig,
    TransportConfig,
    UATConfig,
)


def test_media_capabilities_default_all_true():
    mc = MediaCapabilities()
    assert mc.image and mc.audio and mc.video and mc.file and mc.sticker


def test_name_cache_defaults_match_spec():
    c = NameCacheConfig()
    assert c.enabled and c.max_size == 2000 and c.ttl_seconds == 24 * 3600


def test_inbound_config_defaults():
    ib = InboundConfig()
    assert ib.expand_merge_forward is True
    assert ib.fetch_interactive_card is True
    assert ib.reaction_notifications == "own"
    assert ib.merge_forward_max_depth == 3
    assert ib.merge_forward_max_items == 50


def test_outbound_config_defaults():
    ob = OutboundConfig()
    assert ob.reply_mode == "auto"
    assert ob.text_chunk_limit == 3500  # node-aligned (DEFAULT_CHUNK_LIMIT)
    assert ob.chunk_mode == "newline"
    assert ob.markdown_converter.enabled is True
    assert ob.markdown_converter.table_mode == "off"
    assert ob.ssrf_allowlist is None
    assert isinstance(ob.retry, RetryConfig)
    assert ob.retry.max_attempts == 3


def test_stream_throttle_defaults():
    t = StreamThrottleConfig()
    assert t.min_chars == 20 and t.max_chars == 200 and t.idle_ms == 300


def test_footer_config_all_off_by_default():
    f = FooterConfig()
    assert not any([f.status, f.elapsed, f.tokens, f.model, f.cache, f.context])


def test_dedup_config_defaults():
    d = DedupConfig()
    assert d.enabled is True
    assert d.ttl_seconds == 12 * 3600
    assert d.max_entries == 5000
    assert d.sweep_seconds == 5 * 60


def test_uat_config_defaults():
    u = UATConfig()
    assert u.refresh_before_expiry_seconds == 300
    assert u.device_poll_interval_seconds == 5
    assert u.allowed_scopes is None
    assert u.blocked_scopes is None


def test_transport_config_default_ws():
    t = TransportConfig()
    assert t.kind == "ws"
    assert t.auto_reconnect is True


def test_policy_config_defaults():
    p = PolicyConfig()
    assert p.dm_policy == "open"
    assert p.group_policy == "open"
    assert p.require_mention is True
    assert p.respond_to_mention_all is False
    assert p.allow_from is None
    assert p.group_overrides == {}


def test_group_override_all_fields_optional():
    o = GroupOverride()
    assert o.policy is None and o.enabled is None


def test_safety_config_nests_dedup_and_batch():
    s = SafetyConfig()
    assert isinstance(s.dedup, DedupConfig)
    # text_batch / chat_queue live in safety.types; we just verify the
    # nesting is present without pinning their class names here.
    assert s.text_batch is not None
    assert s.chat_queue is not None
    assert s.stale_message_window_ms == 30 * 60 * 1000


def test_channel_config_top_level_areas():
    c = ChannelConfig()
    assert c.app_id == "" and c.app_secret == ""
    assert c.encrypt_key is None and c.verification_token is None
    assert isinstance(c.transport, TransportConfig)
    assert isinstance(c.policy, PolicyConfig)
    assert isinstance(c.safety, SafetyConfig)
    assert isinstance(c.inbound, InboundConfig)
    assert isinstance(c.outbound, OutboundConfig)
    assert isinstance(c.uat, UATConfig)


def test_per_chat_reply_mode_defaults():
    m = PerChatReplyMode()
    assert m.default == "auto"
    assert m.dm is None and m.group is None


def test_markdown_converter_table_mode_override():
    mc = MarkdownConverter(enabled=False, table_mode="bullets")
    assert mc.enabled is False
    assert mc.table_mode == "bullets"


def test_retry_config_defaults():
    r = RetryConfig()
    assert r.max_attempts == 3
    assert r.base_delay_ms == 500
