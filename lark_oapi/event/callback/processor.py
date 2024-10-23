from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type

from lark_oapi.event.processor import ICallBackProcessor
from .model.p2_card_action_tigger import P2CardActionTigger, P2CardActionTiggerResponse
from .model.p2_url_preview_get import P2URLPreviewGet, P2URLPreviewGetResponse


class P2CardActionTiggerProcessor(ICallBackProcessor[P2CardActionTigger]):
    def __init__(self, f: Callable[[P2CardActionTigger], P2CardActionTiggerResponse]):
        self.f = f

    def type(self) -> Type[P2CardActionTigger]:
        return P2CardActionTigger

    def do(self, data: P2CardActionTigger) -> P2CardActionTiggerResponse:
        return self.f(data)


class P2URLPreviewGetProcessor(ICallBackProcessor[P2URLPreviewGet]):
    def __init__(self, f: Callable[[P2URLPreviewGet], P2URLPreviewGetResponse]):
        self.f = f

    def type(self) -> Type[P2URLPreviewGet]:
        return P2URLPreviewGet

    def do(self, data: P2URLPreviewGet) -> P2URLPreviewGetResponse:
        return self.f(data)
