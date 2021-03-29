# -*- coding: UTF-8 -*-

import time

from ...config import Config
from ...consts import APP_TYPE_INTERNAL
from ...context import Context
from ..handler.manager import Manager
from ..model.event import BaseEvent, BaseEventData
import attr


@attr.s
class AppTicketEventData(BaseEventData):
    app_ticket = attr.ib(type=str, default='')


@attr.s
class AppTicketEvent(BaseEvent):
    event = attr.ib(type=AppTicketEventData, default=None)


def app_ticket_event_callback(ctx, conf, event):
    # type: (Context, Config, AppTicketEvent) -> None
    key = "%s-%s" % ('app_ticket', conf.app_settings.app_id)
    val = event.event.app_ticket
    expire = int(time.time()) + (12 * 60 * 60)
    try:
        conf.store.set(key, val, expire)
    except Exception as e:
        conf.logger.warn('set %s=%s, expire=%d into storage occurred an error:%s' % (key, val, expire, e.__str__()))


def set_app_ticket_event_handler(conf):
    # type: (Config) -> None
    if conf.app_settings.app_type == APP_TYPE_INTERNAL:
        return
    Manager.set_event_callback(conf, 'app_ticket', app_ticket_event_callback, clazz=AppTicketEvent)
