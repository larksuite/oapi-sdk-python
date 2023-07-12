from typing import Optional, Dict


class RequestOption(object):
    def __init__(self):
        self.tenant_key: Optional[str] = None  # 租户key, app_type = ISV 时需配置
        self.user_access_token: Optional[str] = None
        self.tenant_access_token: Optional[str] = None
        self.app_access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}
