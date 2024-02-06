# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .email_alias import EmailAlias


class CreateMailgroupAliasResponseBody(object):
    _types = {
        "mailgroup_alias": EmailAlias,
    }

    def __init__(self, d=None):
        self.mailgroup_alias: Optional[EmailAlias] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateMailgroupAliasResponseBodyBuilder":
        return CreateMailgroupAliasResponseBodyBuilder()


class CreateMailgroupAliasResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_mailgroup_alias_response_body = CreateMailgroupAliasResponseBody()

    def mailgroup_alias(self, mailgroup_alias: EmailAlias) -> "CreateMailgroupAliasResponseBodyBuilder":
        self._create_mailgroup_alias_response_body.mailgroup_alias = mailgroup_alias
        return self

    def build(self) -> "CreateMailgroupAliasResponseBody":
        return self._create_mailgroup_alias_response_body