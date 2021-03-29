# -*- coding: UTF-8 -*-


from typing import Any, Callable, Dict, Union

from ...config import Config
from ...context import Context
from ..model.event import HTTPEvent


class Manager(object):
    """
    This handler manager maintains user-defined handler which can be called when webhook requests was triggered
    """

    event_callback_map = \
        {}  # type: Dict[str, Callable[[Context, Config, HTTPEvent], Any]]

    event_type_map = \
        {}  # type: Dict[str, Any]

    @staticmethod
    def set_event_callback(conf, event_type, handler, clazz):
        # type: (Config, str, Callable[[Context, Config, Any], Any], Any) -> None

        key = Manager.__key(conf.app_settings.app_id, event_type)
        Manager.event_callback_map[key] = handler
        Manager.event_type_map[key] = clazz

    @staticmethod
    def get_event_callback(conf, event_type):
        # type: (Config, str) -> Union[Callable[[Context, Config, HTTPEvent], Any], None]

        key = Manager.__key(conf.app_settings.app_id, event_type)
        return Manager.event_callback_map.get(key)

    @staticmethod
    def get_event_type(conf, event_type):
        # type: (Config, str) -> Union[Any, None]

        key = Manager.__key(conf.app_settings.app_id, event_type)
        return Manager.event_type_map.get(key)

    @staticmethod
    def __key(app_id, event_type):  # type: (str, str) -> str
        key = '%s-%s' % (app_id, event_type)
        return key
