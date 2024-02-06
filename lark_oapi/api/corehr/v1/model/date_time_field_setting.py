# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class DateTimeFieldSetting(object):
    _types = {
        "date_time_type": int,
    }

    def __init__(self, d=None):
        self.date_time_type: Optional[int] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DateTimeFieldSettingBuilder":
        return DateTimeFieldSettingBuilder()


class DateTimeFieldSettingBuilder(object):
    def __init__(self) -> None:
        self._date_time_field_setting = DateTimeFieldSetting()

    def date_time_type(self, date_time_type: int) -> "DateTimeFieldSettingBuilder":
        self._date_time_field_setting.date_time_type = date_time_type
        return self

    def build(self) -> "DateTimeFieldSetting":
        return self._date_time_field_setting