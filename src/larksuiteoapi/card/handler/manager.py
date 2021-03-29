# -*- coding: UTF-8 -*-

from typing import Callable, Dict, Union

from ..model.card import Card
from ...config import Config
from ...context import Context


class Manager(object):
    """
    This handler manager maintains user-defined handler which can be called when webhook requests was triggered
    """

    app_id_to_handler = {}  # type: Dict[str, Callable[[Context, Config, Card], Union[None, Dict]]]

    @staticmethod
    def set_callback(conf, handler):
        # type: (Config, Callable[[Context, Config,  Card], Union[None, Dict]]) -> None
        Manager.app_id_to_handler[conf.app_settings.app_id] = handler

    @staticmethod
    def get_callback(conf):
        # type: (Config) -> Union[Callable[[Context, Config, Card], Union[None, Dict]], None]
        app_id = conf.app_settings.app_id
        return Manager.app_id_to_handler.get(app_id)
