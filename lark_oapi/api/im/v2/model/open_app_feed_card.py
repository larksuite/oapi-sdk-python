# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .open_feed_status_label import OpenFeedStatusLabel
from .open_app_feed_card_buttons import OpenAppFeedCardButtons
from .open_app_feed_link import OpenAppFeedLink
from .app_feed_notify import AppFeedNotify


class OpenAppFeedCard(object):
    _types = {
        "biz_id": str,
        "title": str,
        "avatar_key": str,
        "preview": str,
        "status_label": OpenFeedStatusLabel,
        "buttons": OpenAppFeedCardButtons,
        "link": OpenAppFeedLink,
        "time_sensitive": bool,
        "notify": AppFeedNotify,
    }

    def __init__(self, d=None):
        self.biz_id: Optional[str] = None
        self.title: Optional[str] = None
        self.avatar_key: Optional[str] = None
        self.preview: Optional[str] = None
        self.status_label: Optional[OpenFeedStatusLabel] = None
        self.buttons: Optional[OpenAppFeedCardButtons] = None
        self.link: Optional[OpenAppFeedLink] = None
        self.time_sensitive: Optional[bool] = None
        self.notify: Optional[AppFeedNotify] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "OpenAppFeedCardBuilder":
        return OpenAppFeedCardBuilder()


class OpenAppFeedCardBuilder(object):
    def __init__(self) -> None:
        self._open_app_feed_card = OpenAppFeedCard()

    def biz_id(self, biz_id: str) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.biz_id = biz_id
        return self

    def title(self, title: str) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.title = title
        return self

    def avatar_key(self, avatar_key: str) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.avatar_key = avatar_key
        return self

    def preview(self, preview: str) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.preview = preview
        return self

    def status_label(self, status_label: OpenFeedStatusLabel) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.status_label = status_label
        return self

    def buttons(self, buttons: OpenAppFeedCardButtons) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.buttons = buttons
        return self

    def link(self, link: OpenAppFeedLink) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.link = link
        return self

    def time_sensitive(self, time_sensitive: bool) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.time_sensitive = time_sensitive
        return self

    def notify(self, notify: AppFeedNotify) -> "OpenAppFeedCardBuilder":
        self._open_app_feed_card.notify = notify
        return self

    def build(self) -> "OpenAppFeedCard":
        return self._open_app_feed_card