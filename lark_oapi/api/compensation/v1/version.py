from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.archive: Archive = Archive(config)
        self.change_reason: ChangeReason = ChangeReason(config)
        self.indicator: Indicator = Indicator(config)
        self.item: Item = Item(config)
        self.item_category: ItemCategory = ItemCategory(config)
        self.plan: Plan = Plan(config)
