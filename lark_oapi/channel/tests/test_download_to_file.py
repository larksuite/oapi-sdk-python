"""Tests for FeishuChannel.download_resource_to_file."""

from unittest.mock import patch

import pytest

from lark_oapi.channel import FeishuChannel, FeishuChannelError, FeishuChannelErrorCode


@pytest.mark.asyncio
async def test_success_returns_existing_path(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    fake_bytes = b"\x89PNG\r\n\x1a\nrest"

    async def fake_download(*args, **kwargs):
        return fake_bytes, "image/png"

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="img_xyz",
            resource_type="image",
            message_id="om_test",
            dest_dir=tmp_path,
        )

    assert path.exists()
    assert path.parent == tmp_path
    assert path.read_bytes() == fake_bytes
    # Suffix from content-type "image/png"
    assert path.suffix == ".png"


@pytest.mark.asyncio
async def test_dest_dir_is_auto_mkdir(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    target = tmp_path / "deep" / "nested" / "dir"
    assert not target.exists()

    async def fake_download(*args, **kwargs):
        return b"data", "application/pdf"

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="f1", resource_type="file", message_id="om_x", dest_dir=target
        )
    assert path.parent == target
    assert path.suffix == ".pdf"


@pytest.mark.asyncio
async def test_failure_raises_download_failed(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return None, None  # failure path

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        with pytest.raises(FeishuChannelError) as excinfo:
            await ch.download_resource_to_file(
                file_key="bad", resource_type="image", message_id="om_x", dest_dir=tmp_path
            )
        assert excinfo.value.code == FeishuChannelErrorCode.DOWNLOAD_FAILED


@pytest.mark.asyncio
async def test_explicit_file_name_overrides_inferred(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"data", "image/jpeg"

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="k", resource_type="image", message_id="m",
            dest_dir=tmp_path, file_name="custom.bin",
        )
    assert path.name == "custom.bin"


@pytest.mark.asyncio
async def test_explicit_file_name_cannot_escape_dest_dir(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"data", "image/jpeg"

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        with pytest.raises(FeishuChannelError) as excinfo:
            await ch.download_resource_to_file(
                file_key="k",
                resource_type="image",
                message_id="m",
                dest_dir=tmp_path,
                file_name="../escape.bin",
            )

    assert excinfo.value.code == FeishuChannelErrorCode.DOWNLOAD_FAILED
    assert not (tmp_path.parent / "escape.bin").exists()


@pytest.mark.asyncio
async def test_default_file_name_cannot_escape_dest_dir(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"data", "image/jpeg"

    with patch(
            "lark_oapi.channel._api_helpers.download_media_with_meta",
            side_effect=fake_download,
    ):
        with pytest.raises(FeishuChannelError) as excinfo:
            await ch.download_resource_to_file(
                file_key="../escape",
                resource_type="image",
                message_id="m",
                dest_dir=tmp_path,
            )

    assert excinfo.value.code == FeishuChannelErrorCode.DOWNLOAD_FAILED
    assert not (tmp_path.parent / "escape.jpg").exists()
