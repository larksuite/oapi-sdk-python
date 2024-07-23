# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class AilyKnowledgeFolder(object):
    _types = {
        "title": str,
        "token": str,
        "url": str,
    }

    def __init__(self, d=None):
        self.title: Optional[str] = None
        self.token: Optional[str] = None
        self.url: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AilyKnowledgeFolderBuilder":
        return AilyKnowledgeFolderBuilder()


class AilyKnowledgeFolderBuilder(object):
    def __init__(self) -> None:
        self._aily_knowledge_folder = AilyKnowledgeFolder()

    def title(self, title: str) -> "AilyKnowledgeFolderBuilder":
        self._aily_knowledge_folder.title = title
        return self

    def token(self, token: str) -> "AilyKnowledgeFolderBuilder":
        self._aily_knowledge_folder.token = token
        return self

    def url(self, url: str) -> "AilyKnowledgeFolderBuilder":
        self._aily_knowledge_folder.url = url
        return self

    def build(self) -> "AilyKnowledgeFolder":
        return self._aily_knowledge_folder