# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .task_dependency import TaskDependency


class RemoveDependenciesTaskRequestBody(object):
    _types = {
        "dependencies": List[TaskDependency],
    }

    def __init__(self, d=None):
        self.dependencies: Optional[List[TaskDependency]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RemoveDependenciesTaskRequestBodyBuilder":
        return RemoveDependenciesTaskRequestBodyBuilder()


class RemoveDependenciesTaskRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._remove_dependencies_task_request_body = RemoveDependenciesTaskRequestBody()

    def dependencies(self, dependencies: List[TaskDependency]) -> "RemoveDependenciesTaskRequestBodyBuilder":
        self._remove_dependencies_task_request_body.dependencies = dependencies
        return self

    def build(self) -> "RemoveDependenciesTaskRequestBody":
        return self._remove_dependencies_task_request_body
