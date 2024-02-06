# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .department import Department


class ApplicationOfferBasicInfoUser(object):
    _types = {
        "id": str,
        "name": str,
        "en_name": str,
        "avatar": str,
        "department": Department,
        "timezone": str,
        "phone": str,
        "email": str,
        "in_app_scope": bool,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.en_name: Optional[str] = None
        self.avatar: Optional[str] = None
        self.department: Optional[Department] = None
        self.timezone: Optional[str] = None
        self.phone: Optional[str] = None
        self.email: Optional[str] = None
        self.in_app_scope: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ApplicationOfferBasicInfoUserBuilder":
        return ApplicationOfferBasicInfoUserBuilder()


class ApplicationOfferBasicInfoUserBuilder(object):
    def __init__(self) -> None:
        self._application_offer_basic_info_user = ApplicationOfferBasicInfoUser()

    def id(self, id: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.id = id
        return self

    def name(self, name: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.name = name
        return self

    def en_name(self, en_name: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.en_name = en_name
        return self

    def avatar(self, avatar: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.avatar = avatar
        return self

    def department(self, department: Department) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.department = department
        return self

    def timezone(self, timezone: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.timezone = timezone
        return self

    def phone(self, phone: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.phone = phone
        return self

    def email(self, email: str) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.email = email
        return self

    def in_app_scope(self, in_app_scope: bool) -> "ApplicationOfferBasicInfoUserBuilder":
        self._application_offer_basic_info_user.in_app_scope = in_app_scope
        return self

    def build(self) -> "ApplicationOfferBasicInfoUser":
        return self._application_offer_basic_info_user