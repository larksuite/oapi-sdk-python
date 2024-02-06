# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .website_delivery_customized_data import WebsiteDeliveryCustomizedData


class WebsiteDeliveryCustomizedDataParent(object):
    _types = {
        "object_id": str,
        "children": List[WebsiteDeliveryCustomizedData],
    }

    def __init__(self, d=None):
        self.object_id: Optional[str] = None
        self.children: Optional[List[WebsiteDeliveryCustomizedData]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "WebsiteDeliveryCustomizedDataParentBuilder":
        return WebsiteDeliveryCustomizedDataParentBuilder()


class WebsiteDeliveryCustomizedDataParentBuilder(object):
    def __init__(self) -> None:
        self._website_delivery_customized_data_parent = WebsiteDeliveryCustomizedDataParent()

    def object_id(self, object_id: str) -> "WebsiteDeliveryCustomizedDataParentBuilder":
        self._website_delivery_customized_data_parent.object_id = object_id
        return self

    def children(self, children: List[WebsiteDeliveryCustomizedData]) -> "WebsiteDeliveryCustomizedDataParentBuilder":
        self._website_delivery_customized_data_parent.children = children
        return self

    def build(self) -> "WebsiteDeliveryCustomizedDataParent":
        return self._website_delivery_customized_data_parent