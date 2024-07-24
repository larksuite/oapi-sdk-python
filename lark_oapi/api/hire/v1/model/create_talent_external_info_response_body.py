# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .talent_external_info import TalentExternalInfo


class CreateTalentExternalInfoResponseBody(object):
    _types = {
        "external_info": TalentExternalInfo,
    }

    def __init__(self, d=None):
        self.external_info: Optional[TalentExternalInfo] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateTalentExternalInfoResponseBodyBuilder":
        return CreateTalentExternalInfoResponseBodyBuilder()


class CreateTalentExternalInfoResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_talent_external_info_response_body = CreateTalentExternalInfoResponseBody()

    def external_info(self, external_info: TalentExternalInfo) -> "CreateTalentExternalInfoResponseBodyBuilder":
        self._create_talent_external_info_response_body.external_info = external_info
        return self

    def build(self) -> "CreateTalentExternalInfoResponseBody":
        return self._create_talent_external_info_response_body
