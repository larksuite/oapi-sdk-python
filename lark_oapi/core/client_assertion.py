from dataclasses import dataclass
from typing import Optional, Protocol
from urllib.parse import urlparse

from lark_oapi.core.const import FEISHU_DOMAIN, FEISHU_OAUTH_DOMAIN, LARK_DOMAIN, LARK_OAUTH_DOMAIN


@dataclass
class TargetInfo:
    target_service: str
    target_prefix: str = ""


@dataclass
class ClientAssertionToken:
    value: str
    target_info: Optional[TargetInfo] = None


class ClientAssertionProvider(Protocol):
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        raise NotImplementedError


def _normalize_base_url(base_url: str) -> str:
    if "://" not in base_url:
        base_url = "https://" + base_url
    return base_url.rstrip("/")


def extract_aud_from_url(raw_url: str) -> str:
    if "://" not in raw_url:
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    if parsed.netloc:
        return parsed.netloc
    if parsed.path and "/" not in parsed.path:
        return parsed.path
    raise ValueError(f"invalid url: {raw_url}")


def resolve_oauth_base_url(config) -> str:
    oauth_base_url = getattr(config, "oauth_base_url", None)
    if oauth_base_url:
        return _normalize_base_url(oauth_base_url)

    aud = extract_aud_from_url(config.domain)
    if aud == extract_aud_from_url(FEISHU_DOMAIN):
        return FEISHU_OAUTH_DOMAIN
    if aud == extract_aud_from_url(LARK_DOMAIN):
        return LARK_OAUTH_DOMAIN
    raise ValueError(
        "OAuthBaseUrl is not configured. When domain is set to a non-default value "
        "(neither open.feishu.cn nor open.larksuite.com), configure oauth_base_url explicitly."
    )


def resolve_oauth_aud(config) -> str:
    return extract_aud_from_url(resolve_oauth_base_url(config))


def build_proxy_url(target_info: TargetInfo, api_path: str) -> str:
    target_service = target_info.target_service
    if "://" not in target_service:
        target_service = "https://" + target_service
    return target_service + target_info.target_prefix + api_path
