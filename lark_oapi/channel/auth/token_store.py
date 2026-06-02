"""TokenStore interface + two built-in implementations.

- `InMemoryTokenStore`: dict-based, process-local, ephemeral. Default.
- `FileTokenStore`: plaintext JSON file. *Dev only* — constructor warns
  loudly.

Production users should implement their own TokenStore backed by Vault /
KMS / managed database; see the `TokenStore` protocol below.
"""

import asyncio
import json
import os
import threading
import warnings
from typing import Dict, Optional, Protocol, runtime_checkable

from lark_oapi.core.log import logger

from ..types import UAT


@runtime_checkable
class TokenStore(Protocol):
    """Async interface for UAT storage."""

    async def get(self, user_id: str) -> Optional[UAT]: ...

    async def set(self, user_id: str, token: UAT) -> None: ...

    async def delete(self, user_id: str) -> None: ...


class InMemoryTokenStore:
    """Thread-safe dict-backed TokenStore. Loses state when the process dies."""

    def __init__(self) -> None:
        self._data: Dict[str, UAT] = {}
        self._lock = threading.Lock()

    async def get(self, user_id: str) -> Optional[UAT]:
        with self._lock:
            return self._data.get(user_id)

    async def set(self, user_id: str, token: UAT) -> None:
        with self._lock:
            self._data[user_id] = token

    async def delete(self, user_id: str) -> None:
        with self._lock:
            self._data.pop(user_id, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class FileTokenStore:
    """Plaintext JSON file TokenStore — development only.

    Persists UATs across process restarts so you don't have to re-authorize on
    every run. Emits a prominent warning so anybody reading the logs in a
    production environment realizes this is not for them.
    """

    def __init__(self, path: str) -> None:
        warnings.warn(
            "FileTokenStore is not for production. Use a custom TokenStore "
            "backed by Vault / KMS / encrypted database.",
            UserWarning,
            stacklevel=2,
        )
        logger.warning(
            "FileTokenStore: storing UATs in plaintext at %s — dev only",
            path,
        )
        self._path = path
        # Defer lock creation to first use so the lock binds to the event loop
        # that actually performs async I/O, not the loop that happened to be
        # running at construction time (which may be a different loop when the
        # store is shared with FeishuChannel's bg loop).
        self._lock: Optional[asyncio.Lock] = None
        self._mem: Dict[str, UAT] = self._load()

    def _load(self) -> Dict[str, UAT]:
        if not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            out: Dict[str, UAT] = {}
            for k, v in (raw or {}).items():
                if isinstance(v, dict):
                    out[k] = UAT(
                        access_token=v.get("access_token") or "",
                        refresh_token=v.get("refresh_token"),
                        expires_at=v.get("expires_at"),
                        refresh_expires_at=v.get("refresh_expires_at"),
                        scopes=list(v.get("scopes") or []),
                        open_id=v.get("open_id"),
                        raw=v.get("raw") or {},
                    )
            return out
        except (OSError, ValueError) as e:
            logger.warning("FileTokenStore: failed to load %s: %s", self._path, e)
            return {}

    def _persist(self) -> None:
        serializable = {
            k: {
                "access_token": v.access_token,
                "refresh_token": v.refresh_token,
                "expires_at": v.expires_at,
                "refresh_expires_at": v.refresh_expires_at,
                "scopes": v.scopes,
                "open_id": v.open_id,
                "raw": v.raw,
            }
            for k, v in self._mem.items()
        }
        tmp = self._path + ".tmp"
        # Open with explicit 0o600 permissions so the file is never
        # world-readable on Linux, regardless of the caller's umask. Tokens
        # are sensitive credentials.
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(tmp, flags, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(serializable, fh, ensure_ascii=False, indent=2)
        except Exception:
            # Best-effort cleanup of tmp on failure.
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        os.replace(tmp, self._path)
        # Re-assert permissions on the final file in case `os.replace` didn't
        # preserve them (some filesystems / prior-existing file with looser
        # perms).
        try:
            os.chmod(self._path, 0o600)
        except OSError as e:
            logger.warning(
                "FileTokenStore: failed to chmod 0600 on %s: %s", self._path, e
            )

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get(self, user_id: str) -> Optional[UAT]:
        async with self._get_lock():
            return self._mem.get(user_id)

    async def set(self, user_id: str, token: UAT) -> None:
        async with self._get_lock():
            self._mem[user_id] = token
            # Offload the synchronous JSON write + os.replace to a worker
            # thread so the event loop stays responsive.
            await asyncio.get_running_loop().run_in_executor(None, self._persist)

    async def delete(self, user_id: str) -> None:
        async with self._get_lock():
            self._mem.pop(user_id, None)
            await asyncio.get_running_loop().run_in_executor(None, self._persist)
