# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class CreateMigrationEntity(object):
    _types = {
        "id": str,
        "type": str,
        "location": str,
        "mail_address": str,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.type: Optional[str] = None
        self.location: Optional[str] = None
        self.mail_address: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateMigrationEntityBuilder":
        return CreateMigrationEntityBuilder()


class CreateMigrationEntityBuilder(object):
    def __init__(self) -> None:
        self._create_migration_entity = CreateMigrationEntity()

    def id(self, id: str) -> "CreateMigrationEntityBuilder":
        self._create_migration_entity.id = id
        return self

    def type(self, type: str) -> "CreateMigrationEntityBuilder":
        self._create_migration_entity.type = type
        return self

    def location(self, location: str) -> "CreateMigrationEntityBuilder":
        self._create_migration_entity.location = location
        return self

    def mail_address(self, mail_address: str) -> "CreateMigrationEntityBuilder":
        self._create_migration_entity.mail_address = mail_address
        return self

    def build(self) -> "CreateMigrationEntity":
        return self._create_migration_entity
