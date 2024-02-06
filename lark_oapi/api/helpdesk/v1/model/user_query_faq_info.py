# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class UserQueryFaqInfo(object):
    _types = {
        "id": str,
        "score": float,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.score: Optional[float] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UserQueryFaqInfoBuilder":
        return UserQueryFaqInfoBuilder()


class UserQueryFaqInfoBuilder(object):
    def __init__(self) -> None:
        self._user_query_faq_info = UserQueryFaqInfo()

    def id(self, id: str) -> "UserQueryFaqInfoBuilder":
        self._user_query_faq_info.id = id
        return self

    def score(self, score: float) -> "UserQueryFaqInfoBuilder":
        self._user_query_faq_info.score = score
        return self

    def build(self) -> "UserQueryFaqInfo":
        return self._user_query_faq_info