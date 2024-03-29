# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .verification import Verification


class GetVerificationResponseBody(object):
    _types = {
        "verification": Verification,
    }

    def __init__(self, d=None):
        self.verification: Optional[Verification] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "GetVerificationResponseBodyBuilder":
        return GetVerificationResponseBodyBuilder()


class GetVerificationResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._get_verification_response_body = GetVerificationResponseBody()

    def verification(self, verification: Verification) -> "GetVerificationResponseBodyBuilder":
        self._get_verification_response_body.verification = verification
        return self

    def build(self) -> "GetVerificationResponseBody":
        return self._get_verification_response_body
