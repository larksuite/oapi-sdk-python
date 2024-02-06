# Code generated by Lark OpenAPI.

from typing import Any, Optional, IO

from lark_oapi.core.construct import init


class UploadPartFileRequestBody(object):
    _types = {
        "upload_id": str,
        "seq": int,
        "size": int,
        "checksum": str,
        "file": IO[Any],
    }

    def __init__(self, d=None):
        self.upload_id: Optional[str] = None
        self.seq: Optional[int] = None
        self.size: Optional[int] = None
        self.checksum: Optional[str] = None
        self.file: Optional[IO[Any]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UploadPartFileRequestBodyBuilder":
        return UploadPartFileRequestBodyBuilder()


class UploadPartFileRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._upload_part_file_request_body = UploadPartFileRequestBody()

    def upload_id(self, upload_id: str) -> "UploadPartFileRequestBodyBuilder":
        self._upload_part_file_request_body.upload_id = upload_id
        return self

    def seq(self, seq: int) -> "UploadPartFileRequestBodyBuilder":
        self._upload_part_file_request_body.seq = seq
        return self

    def size(self, size: int) -> "UploadPartFileRequestBodyBuilder":
        self._upload_part_file_request_body.size = size
        return self

    def checksum(self, checksum: str) -> "UploadPartFileRequestBodyBuilder":
        self._upload_part_file_request_body.checksum = checksum
        return self

    def file(self, file: IO[Any]) -> "UploadPartFileRequestBodyBuilder":
        self._upload_part_file_request_body.file = file
        return self

    def build(self) -> "UploadPartFileRequestBody":
        return self._upload_part_file_request_body