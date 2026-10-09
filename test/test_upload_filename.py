import io
from email import policy
from email.parser import BytesParser

import httpx
import pytest
from requests_toolbelt import MultipartEncoder

from lark_oapi.api.agent.v1.model.create_file_request_body import CreateFileRequestBody
from lark_oapi.core.utils.files import Files


def parts(content_type, content):
    message = BytesParser(policy=policy.default).parsebytes(
        ("Content-Type: " + content_type + "\r\n\r\n").encode() + content
    )
    return {part.get_param("name", header="content-disposition"): part
            for part in message.iter_parts()}


@pytest.mark.parametrize("name", ["report.txt", "中文报告.txt"])
@pytest.mark.parametrize("use_tuple", [False, True])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_upload_filename_override(name, use_tuple, asynchronous):
    stream = io.BytesIO(b"contents")
    file = ("original.txt", stream, "text/plain") if use_tuple else stream
    body = CreateFileRequestBody.builder().file(file).filename(name).build()
    if asynchronous:
        files = Files.extract_files(body)
        request = httpx.Request("POST", "https://example.test", files=files,
                                data={"filename": body.filename})
        content_type, content = request.headers["content-type"], request.read()
    else:
        encoder = MultipartEncoder(Files.parse_form_data(body))
        content_type, content = encoder.content_type, encoder.to_string()
        assert body.file is file
    fields = parts(content_type, content)
    assert fields["file"].get_filename() == name
    assert fields["file"].get_payload(decode=True) == b"contents"
    assert fields["filename"].get_payload(decode=True).decode() == name
    if use_tuple:
        assert fields["file"].get_content_type() == "text/plain"


def test_sync_file_object_has_filename(tmp_path):
    path = tmp_path / "original.txt"
    path.write_bytes(b"contents")
    with path.open("rb") as stream:
        encoder = MultipartEncoder(Files.parse_form_data({"file": stream}))
        assert parts(encoder.content_type, encoder.to_string())["file"].get_filename() == path.name


@pytest.mark.parametrize("name", ["../report.txt", "sub/report.txt", "sub\\report.txt", "bad\r\nname", "bad\x00name"])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_reject_unsafe_explicit_filename(name, asynchronous):
    body = CreateFileRequestBody.builder().file(io.BytesIO(b"data")).filename(name).build()
    with pytest.raises(ValueError, match="upload filename"):
        (Files.extract_files if asynchronous else Files.parse_form_data)(body)


@pytest.mark.parametrize("asynchronous", [False, True])
def test_unmapped_filename_does_not_override_file(asynchronous):
    class OtherBody:
        def __init__(self):
            self.file = ("original.txt", io.BytesIO(b"data"), "text/plain")
            self.filename = "business-name.txt"
    body = OtherBody()
    values = (Files.extract_files if asynchronous else Files.parse_form_data)(body)
    assert values["file"][0] == "original.txt"
    assert values["file"][2] == "text/plain"


@pytest.mark.parametrize("name", [None, ""])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_unset_filename_keeps_stream_name(name, asynchronous):
    stream = io.BytesIO(b"data")
    stream.name = "/local/original.txt"
    body = CreateFileRequestBody.builder().file(stream).filename(name).build()
    values = (Files.extract_files if asynchronous else Files.parse_form_data)(body)
    assert values["file"][0] == "original.txt"
