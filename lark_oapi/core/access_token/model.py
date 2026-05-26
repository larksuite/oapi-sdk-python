from dataclasses import dataclass
from typing import Optional

from lark_oapi.core.model import RawResponse


@dataclass
class AccessTokenResponse:
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None
    scope: Optional[str] = None
    raw: Optional[RawResponse] = None


def value_if_not_empty(value):
    return value if value not in ("", 0, None) else None
