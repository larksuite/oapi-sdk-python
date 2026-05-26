from typing import Any, List, Optional

from lark_oapi.core import AppType, LogLevel
from lark_oapi.core.cache import ICache
from lark_oapi.core.const import FEISHU_DOMAIN


class Config(object):
    def __init__(self) -> None:
        self.app_id: Optional[str] = None
        self.app_secret: Optional[str] = None
        self.domain: str = FEISHU_DOMAIN  # 域名, 默认为 https://open.feishu.cn
        self.oauth_base_url: Optional[str] = None
        self.client_assertion_provider: Optional[Any] = None
        self.timeout: Optional[float] = 30  # client timeout in seconds (default 30s); override via ClientBuilder.timeout()
        self.app_type: AppType = AppType.SELF  # 应用类型, 默认为自建应用; 若设为 ISV 需在 request_option 中配置 tenant_key
        self.enable_set_token: bool = False  # 是否允许手动设置 token, 默认不开启; 开启后需在 request_option 中配置 token
        self.cache: Optional[ICache] = None  # 自定义缓存, 默认使用预置的本地缓存
        self.log_level: LogLevel = LogLevel.WARNING  # 日志级别, 默认为 WARNING
        self.source: Optional[str] = None  # caller identifier, appended to UA as `source/<name>`
        # Internal: sub-modules (e.g. channel) append bare UA tags from here.
        self.extra_ua_tags: Optional[List[str]] = None
