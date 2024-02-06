# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .i18n import I18n


class WebsiteJobPostCustomizedOption(object):
    _types = {
        "key": str,
        "name": I18n,
    }

    def __init__(self, d=None):
        self.key: Optional[str] = None
        self.name: Optional[I18n] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "WebsiteJobPostCustomizedOptionBuilder":
        return WebsiteJobPostCustomizedOptionBuilder()


class WebsiteJobPostCustomizedOptionBuilder(object):
    def __init__(self) -> None:
        self._website_job_post_customized_option = WebsiteJobPostCustomizedOption()

    def key(self, key: str) -> "WebsiteJobPostCustomizedOptionBuilder":
        self._website_job_post_customized_option.key = key
        return self

    def name(self, name: I18n) -> "WebsiteJobPostCustomizedOptionBuilder":
        self._website_job_post_customized_option.name = name
        return self

    def build(self) -> "WebsiteJobPostCustomizedOption":
        return self._website_job_post_customized_option