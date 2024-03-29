# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .profile_setting_i18n import ProfileSettingI18n
from .profile_setting_i18n import ProfileSettingI18n
from .profile_setting_i18n import ProfileSettingI18n
from .profile_setting_i18n import ProfileSettingI18n
from .profile_setting_custom_field import ProfileSettingCustomField


class ProfileSettingWorkExperience(object):
    _types = {
        "company_organization": ProfileSettingI18n,
        "department": ProfileSettingI18n,
        "start_date": str,
        "end_date": str,
        "job": ProfileSettingI18n,
        "description": ProfileSettingI18n,
        "custom_fields": List[ProfileSettingCustomField],
    }

    def __init__(self, d=None):
        self.company_organization: Optional[ProfileSettingI18n] = None
        self.department: Optional[ProfileSettingI18n] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        self.job: Optional[ProfileSettingI18n] = None
        self.description: Optional[ProfileSettingI18n] = None
        self.custom_fields: Optional[List[ProfileSettingCustomField]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ProfileSettingWorkExperienceBuilder":
        return ProfileSettingWorkExperienceBuilder()


class ProfileSettingWorkExperienceBuilder(object):
    def __init__(self) -> None:
        self._profile_setting_work_experience = ProfileSettingWorkExperience()

    def company_organization(self, company_organization: ProfileSettingI18n) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.company_organization = company_organization
        return self

    def department(self, department: ProfileSettingI18n) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.department = department
        return self

    def start_date(self, start_date: str) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.start_date = start_date
        return self

    def end_date(self, end_date: str) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.end_date = end_date
        return self

    def job(self, job: ProfileSettingI18n) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.job = job
        return self

    def description(self, description: ProfileSettingI18n) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.description = description
        return self

    def custom_fields(self, custom_fields: List[ProfileSettingCustomField]) -> "ProfileSettingWorkExperienceBuilder":
        self._profile_setting_work_experience.custom_fields = custom_fields
        return self

    def build(self) -> "ProfileSettingWorkExperience":
        return self._profile_setting_work_experience
