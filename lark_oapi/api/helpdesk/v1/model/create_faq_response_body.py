# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .faq import Faq


class CreateFaqResponseBody(object):
    _types = {
        "faq": Faq,
    }

    def __init__(self, d=None):
        self.faq: Optional[Faq] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateFaqResponseBodyBuilder":
        return CreateFaqResponseBodyBuilder()


class CreateFaqResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_faq_response_body = CreateFaqResponseBody()

    def faq(self, faq: Faq) -> "CreateFaqResponseBodyBuilder":
        self._create_faq_response_body.faq = faq
        return self

    def build(self) -> "CreateFaqResponseBody":
        return self._create_faq_response_body