# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .task_dependency import TaskDependency


class RemoveDependenciesTaskResponseBody(object):
    _types = {
        "dependencies": List[TaskDependency],
    }

    def __init__(self, d=None):
        self.dependencies: Optional[List[TaskDependency]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RemoveDependenciesTaskResponseBodyBuilder":
        return RemoveDependenciesTaskResponseBodyBuilder()


class RemoveDependenciesTaskResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._remove_dependencies_task_response_body = RemoveDependenciesTaskResponseBody()

    def dependencies(self, dependencies: List[TaskDependency]) -> "RemoveDependenciesTaskResponseBodyBuilder":
        self._remove_dependencies_task_response_body.dependencies = dependencies
        return self

    def build(self) -> "RemoveDependenciesTaskResponseBody":
        return self._remove_dependencies_task_response_body
