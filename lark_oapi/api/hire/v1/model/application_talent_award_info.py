# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class ApplicationTalentAwardInfo(object):
    _types = {
        "id": str,
        "title": str,
        "award_time": int,
        "desc": str,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.title: Optional[str] = None
        self.award_time: Optional[int] = None
        self.desc: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ApplicationTalentAwardInfoBuilder":
        return ApplicationTalentAwardInfoBuilder()


class ApplicationTalentAwardInfoBuilder(object):
    def __init__(self) -> None:
        self._application_talent_award_info = ApplicationTalentAwardInfo()

    def id(self, id: str) -> "ApplicationTalentAwardInfoBuilder":
        self._application_talent_award_info.id = id
        return self

    def title(self, title: str) -> "ApplicationTalentAwardInfoBuilder":
        self._application_talent_award_info.title = title
        return self

    def award_time(self, award_time: int) -> "ApplicationTalentAwardInfoBuilder":
        self._application_talent_award_info.award_time = award_time
        return self

    def desc(self, desc: str) -> "ApplicationTalentAwardInfoBuilder":
        self._application_talent_award_info.desc = desc
        return self

    def build(self) -> "ApplicationTalentAwardInfo":
        return self._application_talent_award_info