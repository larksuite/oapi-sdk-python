# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class Acl(object):
    _types = {
        "access": str,
        "value": str,
        "type": str,
    }

    def __init__(self, d=None):
        self.access: Optional[str] = None
        self.value: Optional[str] = None
        self.type: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AclBuilder":
        return AclBuilder()


class AclBuilder(object):
    def __init__(self) -> None:
        self._acl = Acl()

    def access(self, access: str) -> "AclBuilder":
        self._acl.access = access
        return self

    def value(self, value: str) -> "AclBuilder":
        self._acl.value = value
        return self

    def type(self, type: str) -> "AclBuilder":
        self._acl.type = type
        return self

    def build(self) -> "Acl":
        return self._acl