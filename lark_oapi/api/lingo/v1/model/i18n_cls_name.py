# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class I18nClsName(object):
    _types = {
        "language": int,
        "name": str,
    }

    def __init__(self, d=None):
        self.language: Optional[int] = None
        self.name: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "I18nClsNameBuilder":
        return I18nClsNameBuilder()


class I18nClsNameBuilder(object):
    def __init__(self) -> None:
        self._i18n_cls_name = I18nClsName()

    def language(self, language: int) -> "I18nClsNameBuilder":
        self._i18n_cls_name.language = language
        return self

    def name(self, name: str) -> "I18nClsNameBuilder":
        self._i18n_cls_name.name = name
        return self

    def build(self) -> "I18nClsName":
        return self._i18n_cls_name
