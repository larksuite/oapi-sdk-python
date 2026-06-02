"""Unit tests for inbound/interactive.py (card refetch + v1/v2 detection)."""

import json

import pytest

from lark_oapi.channel.normalize.interactive import (
    _detect_version,
    _extract_card_json,
    _parse_body_content,
    fetch_interactive,
)
from lark_oapi.channel.types import InteractiveContent


# ---- Version detection --------------------------------------------------


def test_detect_v2_by_schema():
    assert _detect_version({"schema": "2.0", "body": {}}) == "v2"


def test_detect_v2_by_body_only():
    assert _detect_version({"body": {"elements": []}}) == "v2"


def test_detect_v1_by_elements():
    assert _detect_version({"elements": [], "config": {}}) == "v1"


def test_detect_v1_by_i18n_elements():
    assert _detect_version({"i18n_elements": {}}) == "v1"


def test_detect_unknown_for_empty():
    assert _detect_version({}) == "unknown"


def test_detect_handles_non_dict():
    assert _detect_version("nonsense") == "unknown"  # type: ignore[arg-type]


def test_detect_unwraps_card_wrapper():
    """Some payloads wrap under a `card` key."""
    assert _detect_version({"card": {"schema": "2.0", "body": {}}}) == "v2"


# ---- Content extraction -------------------------------------------------


def test_parse_body_content_from_string():
    body = {"content": json.dumps({"schema": "2.0", "body": {}})}
    assert _parse_body_content(body) == {"schema": "2.0", "body": {}}


def test_parse_body_content_from_dict():
    direct = {"schema": "2.0", "body": {}}
    body = {"content": direct}
    assert _parse_body_content(body) == direct


def test_parse_body_content_invalid_string_returns_none():
    assert _parse_body_content({"content": "{{bad json"}) is None


def test_parse_body_content_missing_returns_none():
    assert _parse_body_content({}) is None


def test_extract_card_json_from_items_array():
    payload = {
        "data": {
            "items": [
                {"body": {"content": json.dumps({"schema": "2.0", "body": {}})}},
            ],
        },
    }
    assert _extract_card_json(payload) == {"schema": "2.0", "body": {}}


def test_extract_card_json_empty_payload_returns_none():
    assert _extract_card_json({}) is None
    assert _extract_card_json({"data": {"items": []}}) is None


def test_extract_card_json_from_flat_data():
    payload = {"data": {"body": {"content": json.dumps({"schema": "2.0", "body": {}})}}}
    assert _extract_card_json(payload) == {"schema": "2.0", "body": {}}


# ---- fetch_interactive -------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_interactive_success_v2():
    async def fetch(mid):
        return {
            "data": {"items": [{"body": {"content": json.dumps({
                "schema": "2.0",
                "body": {"elements": [{"tag": "markdown", "content": "hello"}]},
            })}}]},
        }

    result = await fetch_interactive("om_1", fetch)
    assert isinstance(result, InteractiveContent)
    assert result.card_version == "v2"


@pytest.mark.asyncio
async def test_fetch_interactive_success_v1():
    async def fetch(mid):
        return {
            "data": {"items": [{"body": {"content": json.dumps({
                "elements": [{"tag": "markdown", "content": "legacy"}],
                "config": {},
            })}}]},
        }

    result = await fetch_interactive("om_1", fetch)
    assert result is not None
    assert result.card_version == "v1"


@pytest.mark.asyncio
async def test_fetch_interactive_sync_fetch_also_accepted():
    """Injected fetcher may return a plain value (not awaitable)."""

    def fetch(mid):
        return {"data": {"items": [{"body": {"content": json.dumps({"schema": "2.0", "body": {}})}}]}}

    result = await fetch_interactive("om_1", fetch)
    assert result and result.card_version == "v2"


@pytest.mark.asyncio
async def test_fetch_interactive_fetcher_raises_returns_none():
    async def fetch(mid):
        raise RuntimeError("network")

    assert await fetch_interactive("om_1", fetch) is None


@pytest.mark.asyncio
async def test_fetch_interactive_empty_response_returns_none():
    async def fetch(mid):
        return None

    assert await fetch_interactive("om_1", fetch) is None


@pytest.mark.asyncio
async def test_fetch_interactive_malformed_json_returns_none():
    async def fetch(mid):
        return {"data": {"items": [{"body": {"content": "{{{"}}]}}

    assert await fetch_interactive("om_1", fetch) is None
