from typing import *

from lark_oapi.core import HttpMethod, AccessTokenType


class BaseRequest(object):
    def __init__(self):
        self.http_method: Optional[HttpMethod] = None
        self.uri: Optional[str] = None
        self.token_types: Set[AccessTokenType] = set()
        self.paths: Dict[str, str] = {}
        self.queries: Dict[str, str] = {}
        self.headers: Dict[str, str] = {}
        self.body: Any = None
