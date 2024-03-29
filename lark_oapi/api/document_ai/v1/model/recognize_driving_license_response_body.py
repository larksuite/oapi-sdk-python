# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .drving_license import DrvingLicense


class RecognizeDrivingLicenseResponseBody(object):
    _types = {
        "driving_license": DrvingLicense,
    }

    def __init__(self, d=None):
        self.driving_license: Optional[DrvingLicense] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RecognizeDrivingLicenseResponseBodyBuilder":
        return RecognizeDrivingLicenseResponseBodyBuilder()


class RecognizeDrivingLicenseResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._recognize_driving_license_response_body = RecognizeDrivingLicenseResponseBody()

    def driving_license(self, driving_license: DrvingLicense) -> "RecognizeDrivingLicenseResponseBodyBuilder":
        self._recognize_driving_license_response_body.driving_license = driving_license
        return self

    def build(self) -> "RecognizeDrivingLicenseResponseBody":
        return self._recognize_driving_license_response_body
