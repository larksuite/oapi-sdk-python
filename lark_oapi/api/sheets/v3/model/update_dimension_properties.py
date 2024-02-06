# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .dimension import Dimension
from .dimension_properties import DimensionProperties


class UpdateDimensionProperties(object):
    _types = {
        "dimension_range": Dimension,
        "properties": DimensionProperties,
    }

    def __init__(self, d=None):
        self.dimension_range: Optional[Dimension] = None
        self.properties: Optional[DimensionProperties] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UpdateDimensionPropertiesBuilder":
        return UpdateDimensionPropertiesBuilder()


class UpdateDimensionPropertiesBuilder(object):
    def __init__(self) -> None:
        self._update_dimension_properties = UpdateDimensionProperties()

    def dimension_range(self, dimension_range: Dimension) -> "UpdateDimensionPropertiesBuilder":
        self._update_dimension_properties.dimension_range = dimension_range
        return self

    def properties(self, properties: DimensionProperties) -> "UpdateDimensionPropertiesBuilder":
        self._update_dimension_properties.properties = properties
        return self

    def build(self) -> "UpdateDimensionProperties":
        return self._update_dimension_properties