# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .migration_entity import MigrationEntity


class MigrationItems(object):
    _types = {
        "task_id": str,
        "task_status": str,
        "entity": MigrationEntity,
        "message": str,
    }

    def __init__(self, d=None):
        self.task_id: Optional[str] = None
        self.task_status: Optional[str] = None
        self.entity: Optional[MigrationEntity] = None
        self.message: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MigrationItemsBuilder":
        return MigrationItemsBuilder()


class MigrationItemsBuilder(object):
    def __init__(self) -> None:
        self._migration_items = MigrationItems()

    def task_id(self, task_id: str) -> "MigrationItemsBuilder":
        self._migration_items.task_id = task_id
        return self

    def task_status(self, task_status: str) -> "MigrationItemsBuilder":
        self._migration_items.task_status = task_status
        return self

    def entity(self, entity: MigrationEntity) -> "MigrationItemsBuilder":
        self._migration_items.entity = entity
        return self

    def message(self, message: str) -> "MigrationItemsBuilder":
        self._migration_items.message = message
        return self

    def build(self) -> "MigrationItems":
        return self._migration_items
