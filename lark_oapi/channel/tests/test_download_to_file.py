"""Tests for FeishuChannel.download_resource_to_file (CR-4)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from lark_oapi.channel import (
    DownloadedResource,
    FeishuChannel,
    FeishuChannelError,
    FeishuChannelErrorCode,
    ResourceDescriptor,
)


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
async def test_explicit_file_name_is_sanitized_and_stays_inside_dest_dir(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"data", "application/octet-stream"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="k",
            resource_type="file",
            message_id="m",
            dest_dir=tmp_path,
            file_name="../escape.txt",
        )

    assert path.parent.resolve() == tmp_path.resolve()
    assert path.read_bytes() == b"data"
    assert not (tmp_path.parent / "escape.txt").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "unsafe_name",
    ["a/b.txt", "a\\b.txt", "", ".", "bad\x00name.txt"],
)
async def test_explicit_file_name_sanitize_edge_cases(tmp_path, unsafe_name):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"data", "text/plain"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="k",
            resource_type="file",
            message_id="m",
            dest_dir=tmp_path,
            file_name=unsafe_name,
        )

    assert path.parent.resolve() == tmp_path.resolve()
    assert path.name not in ("", ".", "..")
    assert "/" not in path.name
    assert "\\" not in path.name
    assert "\x00" not in path.name


@pytest.mark.asyncio
async def test_audio_without_filename_defaults_to_ogg_suffix(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"ogg", None

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        path = await ch.download_resource_to_file(
            file_key="file_audio",
            resource_type="audio",
            message_id="m",
            dest_dir=tmp_path,
        )

    assert path.suffix == ".ogg"


@pytest.mark.asyncio
async def test_download_resource_descriptor_uses_resource_filename(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"pdf", "application/pdf"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        result = await ch.download_resource_descriptor_to_file(
            ResourceDescriptor(type="file", file_key="file_1", file_name="report.pdf"),
            message_id="m",
            dest_dir=tmp_path,
        )

    assert isinstance(result, DownloadedResource)
    assert result.path.name == "report.pdf"
    assert result.path.read_bytes() == b"pdf"
    assert result.resource_type == "file"
    assert result.file_key == "file_1"
    assert result.content_type == "application/pdf"
    assert result.file_name is None


@pytest.mark.asyncio
async def test_download_resource_descriptor_audio_falls_back_to_file(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    calls = []

    async def fake_download(*args, **kwargs):
        calls.append(kwargs["resource_type"])
        if kwargs["resource_type"] == "audio":
            return None, None
        return b"ogg", "voice.ogg"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        result = await ch.download_resource_descriptor_to_file(
            ResourceDescriptor(type="audio", file_key="file_voice"),
            message_id="m",
            dest_dir=tmp_path,
        )

    assert calls == ["audio", "file"]
    assert result.resource_type == "file"
    assert result.content_type is None
    assert result.file_name == "voice.ogg"
    assert result.path.name == "voice.ogg"


@pytest.mark.asyncio
async def test_download_resource_descriptor_video_falls_back_to_file(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    calls = []

    async def fake_download(*args, **kwargs):
        calls.append(kwargs["resource_type"])
        if kwargs["resource_type"] == "video":
            return None, None
        return b"mp4", "clip.mp4"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        result = await ch.download_resource_descriptor_to_file(
            ResourceDescriptor(type="video", file_key="file_video"),
            message_id="m",
            dest_dir=tmp_path,
        )

    assert calls == ["video", "file"]
    assert result.resource_type == "file"
    assert result.content_type is None
    assert result.file_name == "clip.mp4"
    assert result.path.name == "clip.mp4"


@pytest.mark.asyncio
async def test_download_resource_descriptor_keeps_unknown_mime_as_content_type(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"custom", "application/x-custom"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        result = await ch.download_resource_descriptor_to_file(
            ResourceDescriptor(type="file", file_key="file_custom"),
            message_id="m",
            dest_dir=tmp_path,
        )

    assert result.content_type == "application/x-custom"
    assert result.file_name is None
    assert result.path.name == "file_custom.bin"


@pytest.mark.asyncio
async def test_download_resource_descriptor_keeps_valid_unregistered_mime(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return b"haptics", "haptics/ivs"

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        result = await ch.download_resource_descriptor_to_file(
            ResourceDescriptor(type="file", file_key="file_haptic"),
            message_id="m",
            dest_dir=tmp_path,
        )

    assert result.content_type == "haptics/ivs"
    assert result.file_name is None
    assert result.path.name == "file_haptic.bin"


@pytest.mark.asyncio
async def test_download_resource_descriptor_failure_raises_download_failed(tmp_path):
    ch = FeishuChannel(app_id="cli_x", app_secret="x")

    async def fake_download(*args, **kwargs):
        return None, None

    with patch(
        "lark_oapi.channel._api_helpers.download_media_with_meta",
        side_effect=fake_download,
    ):
        with pytest.raises(FeishuChannelError) as excinfo:
            await ch.download_resource_descriptor_to_file(
                ResourceDescriptor(type="audio", file_key="bad"),
                message_id="m",
                dest_dir=tmp_path,
            )

    assert excinfo.value.code == FeishuChannelErrorCode.DOWNLOAD_FAILED
