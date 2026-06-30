import base64
import json
import os
import shlex
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Mapping, MutableMapping, Optional
from urllib.parse import urlencode

from lark_oapi.core.cache import ICache
from lark_oapi.core.client_assertion import ClientAssertionToken, TargetInfo


DEFAULT_ENV_FILES = (".env.e2e", ".env.e2e.example")
_ORIGINAL_GETADDRINFO = None


@dataclass(frozen=True)
class DeployDomains:
    openapi_domain: str
    oauth_base_url: str


ONLINE_DOMAINS = DeployDomains(
    openapi_domain="https://open.feishu.cn",
    oauth_base_url="https://accounts.feishu.cn",
)
BOE_DOMAINS = DeployDomains(
    openapi_domain="https://open.feishu-boe.cn",
    oauth_base_url="https://accounts.feishu-boe.cn",
)


class MemoryCache(ICache):
    def __init__(self) -> None:
        self._data: Dict[str, str] = {}

    def get(self, key: str) -> str:
        return self._data.get(key)

    def set(self, key: str, value: str, expire: int):
        self._data[key] = value


class ModeEnvProvider:
    def __init__(self, mode: str, env: Optional[Mapping[str, str]] = None) -> None:
        if mode not in ("zti", "gdpr"):
            raise ValueError("mode must be zti or gdpr")
        self.mode = mode
        self.env = env if env is not None else os.environ
        self.auds = []

    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        self.auds.append(aud)
        if self.mode == "zti":
            assertion = self.env.get("LARK_ZTI_CLIENT_ASSERTION")
            if not assertion:
                raise RuntimeError("LARK_ZTI_CLIENT_ASSERTION is required")
            return ClientAssertionToken(assertion)

        assertion = self.env.get("LARK_GDPR_CLIENT_ASSERTION")
        if not assertion:
            raise RuntimeError("LARK_GDPR_CLIENT_ASSERTION is required")
        target_service = self.env.get("LARK_GDPR_PROXY_SERVICE")
        target_prefix = self.env.get("LARK_GDPR_PROXY_PREFIX")
        if not target_service or not target_prefix:
            raise RuntimeError("LARK_GDPR_PROXY_SERVICE and LARK_GDPR_PROXY_PREFIX are required")
        if not target_prefix.startswith("/"):
            raise RuntimeError("LARK_GDPR_PROXY_PREFIX must start with /")
        return ClientAssertionToken(assertion, TargetInfo(target_service, target_prefix))


def parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "y", "on"):
        return True
    if normalized in ("0", "false", "no", "n", "off"):
        return False
    return default


def deploy_domains(deploy_env: Optional[str]) -> DeployDomains:
    normalized = (deploy_env or "online").strip().lower()
    if normalized in ("online", "prod", "production", "cn"):
        return ONLINE_DOMAINS
    if normalized == "boe":
        return BOE_DOMAINS
    raise ValueError("LARK_DEPLOY_ENV must be online or boe")


def load_env_file(
        path: Path,
        env: Optional[MutableMapping[str, str]] = None,
        override: bool = False,
) -> bool:
    env = env if env is not None else os.environ
    if not path.exists():
        return False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        parts = shlex.split(line, comments=True, posix=True)
        if not parts or "=" not in parts[0]:
            continue
        key, value = parts[0].split("=", 1)
        if not override and key in env:
            continue
        env[key] = value
    return True


def load_e2e_env(
        root: Optional[Path] = None,
        env: Optional[MutableMapping[str, str]] = None,
        override: bool = False,
) -> Optional[Path]:
    root = root or Path.cwd()
    env = env if env is not None else os.environ
    for name in DEFAULT_ENV_FILES:
        path = root / name
        if load_env_file(path, env=env, override=override):
            return path
    return None


def build_host_override_getaddrinfo(
        original_getaddrinfo: Callable,
        target_host: str,
        target_ip: str,
) -> Callable:
    family = socket.AF_INET6 if ":" in target_ip else socket.AF_INET

    def getaddrinfo(host, port, family_arg=0, type_arg=0, proto_arg=0, flags_arg=0):
        if host == target_host:
            return original_getaddrinfo(target_ip, port, family, type_arg, proto_arg, flags_arg)
        return original_getaddrinfo(host, port, family_arg, type_arg, proto_arg, flags_arg)

    return getaddrinfo


def install_host_resolver_override(target_host: str, target_ip: Optional[str]) -> bool:
    if not target_ip:
        return False

    global _ORIGINAL_GETADDRINFO
    if _ORIGINAL_GETADDRINFO is None:
        _ORIGINAL_GETADDRINFO = socket.getaddrinfo
        socket.getaddrinfo = build_host_override_getaddrinfo(_ORIGINAL_GETADDRINFO, target_host, target_ip)
    return True


def build_authorize_url(
        oauth_base_url: str,
        app_id: str,
        redirect_uri: str,
        scope: str,
        state: str,
) -> str:
    query = urlencode({
        "app_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    })
    return oauth_base_url.rstrip("/") + "/open-apis/authen/v1/authorize?" + query


def decode_jwt_payload_unverified(token: str) -> Dict[str, object]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("invalid jwt")
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode((payload + padding).encode("ascii"))
    return json.loads(decoded.decode("utf-8"))
