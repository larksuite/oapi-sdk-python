# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class CreateBadgeImageResponseBody(object):
    _types = {
        "image_key": str,
    }

    def __init__(self, d=None):
        self.image_key: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateBadgeImageResponseBodyBuilder":
        return CreateBadgeImageResponseBodyBuilder()


class CreateBadgeImageResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_badge_image_response_body = CreateBadgeImageResponseBody()

    def image_key(self, image_key: str) -> "CreateBadgeImageResponseBodyBuilder":
        self._create_badge_image_response_body.image_key = image_key
        return self

    def build(self) -> "CreateBadgeImageResponseBody":
        return self._create_badge_image_response_body