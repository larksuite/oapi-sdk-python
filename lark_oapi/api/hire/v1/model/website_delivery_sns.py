# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .website_delivery_customized_data import WebsiteDeliveryCustomizedData


class WebsiteDeliverySns(object):
    _types = {
        "sns_type": int,
        "customized_data": List[WebsiteDeliveryCustomizedData],
        "link": str,
    }

    def __init__(self, d=None):
        self.sns_type: Optional[int] = None
        self.customized_data: Optional[List[WebsiteDeliveryCustomizedData]] = None
        self.link: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "WebsiteDeliverySnsBuilder":
        return WebsiteDeliverySnsBuilder()


class WebsiteDeliverySnsBuilder(object):
    def __init__(self) -> None:
        self._website_delivery_sns = WebsiteDeliverySns()

    def sns_type(self, sns_type: int) -> "WebsiteDeliverySnsBuilder":
        self._website_delivery_sns.sns_type = sns_type
        return self

    def customized_data(self, customized_data: List[WebsiteDeliveryCustomizedData]) -> "WebsiteDeliverySnsBuilder":
        self._website_delivery_sns.customized_data = customized_data
        return self

    def link(self, link: str) -> "WebsiteDeliverySnsBuilder":
        self._website_delivery_sns.link = link
        return self

    def build(self) -> "WebsiteDeliverySns":
        return self._website_delivery_sns