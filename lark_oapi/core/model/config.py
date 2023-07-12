from typing import Optional

from lark_oapi.core.cache import ICache
from lark_oapi.core.const import FEISHU_DOMAIN
from lark_oapi.core import AppType, LogLevel


class Config(object):
    def __init__(self) -> None:
        self.app_id: Optional[str] = None
        self.app_secret: Optional[str] = None
        self.domain: str = FEISHU_DOMAIN  # 域名
        self.app_type: AppType = AppType.SELF  # 应用类型, ISV 需在 request_option 中配置 tenant_key
        self.app_ticket: Optional[str] = None  # 获取 app_access_token 凭证, app_type = ISV 时需配置
        self.enable_set_token: bool = False  # 允许设置 token, 开启后需在 request_option 中配置 token
        self.cache: Optional[ICache] = None  # 自定义缓存
        self.log_level: LogLevel = LogLevel.INFO
