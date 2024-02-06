# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class SiteResumeSns(object):
    _types = {
        "sns_type": str,
        "link": str,
    }

    def __init__(self, d=None):
        self.sns_type: Optional[str] = None
        self.link: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SiteResumeSnsBuilder":
        return SiteResumeSnsBuilder()


class SiteResumeSnsBuilder(object):
    def __init__(self) -> None:
        self._site_resume_sns = SiteResumeSns()

    def sns_type(self, sns_type: str) -> "SiteResumeSnsBuilder":
        self._site_resume_sns.sns_type = sns_type
        return self

    def link(self, link: str) -> "SiteResumeSnsBuilder":
        self._site_resume_sns.link = link
        return self

    def build(self) -> "SiteResumeSns":
        return self._site_resume_sns