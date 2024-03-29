# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .my_ai_plugin_context import MyAiPluginContext
from .my_ai_av_plugin_upload_object import MyAiAvPluginUploadObject
from .my_ai_av_plugin_context_system_info import MyAiAvPluginContextSystemInfo


class MyAiAvPluginScenarioContext(object):
    _types = {
        "plugins": List[MyAiPluginContext],
        "work_mode": int,
        "scenario": str,
        "session_id": str,
        "upload_objects": List[MyAiAvPluginUploadObject],
        "system_info": MyAiAvPluginContextSystemInfo,
    }

    def __init__(self, d=None):
        self.plugins: Optional[List[MyAiPluginContext]] = None
        self.work_mode: Optional[int] = None
        self.scenario: Optional[str] = None
        self.session_id: Optional[str] = None
        self.upload_objects: Optional[List[MyAiAvPluginUploadObject]] = None
        self.system_info: Optional[MyAiAvPluginContextSystemInfo] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MyAiAvPluginScenarioContextBuilder":
        return MyAiAvPluginScenarioContextBuilder()


class MyAiAvPluginScenarioContextBuilder(object):
    def __init__(self) -> None:
        self._my_ai_av_plugin_scenario_context = MyAiAvPluginScenarioContext()

    def plugins(self, plugins: List[MyAiPluginContext]) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.plugins = plugins
        return self

    def work_mode(self, work_mode: int) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.work_mode = work_mode
        return self

    def scenario(self, scenario: str) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.scenario = scenario
        return self

    def session_id(self, session_id: str) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.session_id = session_id
        return self

    def upload_objects(self, upload_objects: List[MyAiAvPluginUploadObject]) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.upload_objects = upload_objects
        return self

    def system_info(self, system_info: MyAiAvPluginContextSystemInfo) -> "MyAiAvPluginScenarioContextBuilder":
        self._my_ai_av_plugin_scenario_context.system_info = system_info
        return self

    def build(self) -> "MyAiAvPluginScenarioContext":
        return self._my_ai_av_plugin_scenario_context
