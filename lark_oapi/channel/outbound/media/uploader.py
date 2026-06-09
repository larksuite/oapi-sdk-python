"""Media upload helpers — resolve a :class:`MediaSource` to a Lark ``file_key``.

Extracted from :mod:`..sender` so the sender can stay focused on message
composition. Aligned with node-sdk's ``channel/outbound/media/uploader.ts``.

The uploader:
    1. Passes through pre-resolved ``key`` sources unchanged.
    2. Gathers bytes for ``buffer``, ``file``, and ``url`` sources (SSRF-
       guarding URLs by default).
    3. Delegates the actual upload to the :class:`SendDriver`'s
       ``upload_image`` / ``upload_file`` callback.

Runtime failures are surfaced as :class:`FeishuChannelError`; ``None`` is
reserved for caller-constructed "nothing to upload" inputs.
"""

import asyncio
import inspect
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lark_oapi.core.log import logger

from ...errors import FeishuChannelError, FeishuChannelErrorCode
from ...types import MediaSource
from .ssrf_guard import assert_public_url, redact_url_for_log

# 50 MiB default cap on URL-sourced downloads. Prevents an attacker URL that
# returns an unbounded body from exhausting worker RAM. Tune via
# ``_url_download_cap`` on the ``MediaSource`` if callers need a larger cap.
_URL_DOWNLOAD_DEFAULT_CAP = 50 * 1024 * 1024


async def resolve_media_key(
        driver,
        source: Optional[MediaSource],
        kind: str,
        *,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        ssrf_allowlist: Optional[List[str]] = None,
) -> Optional[str]:
    """Return a Lark file_key for ``source``, uploading if needed.

    ``kind`` selects the driver endpoint: ``"image"`` → ``upload_image``,
    anything else → ``upload_file``. ``ssrf_allowlist`` (if given) supplies the
    sender-level default from ``OutboundConfig.ssrf_allowlist``; an explicit
    per-source allowlist still takes precedence.

    **Error propagation.** Three failure modes, each surfaced to the caller
    with a typed :class:`FeishuChannelError` code so the sender can map it
    onto a ``SendResult.fail`` with the right taxonomy instead of the
    previous "empty body" catch-all (which lost the real code / msg):

    - ``UPLOAD_FAILED`` — the upload API returned a non-zero code or the
      underlying transport raised (network / TLS / auth). ``context`` carries
      ``raw_code`` and ``raw_msg`` pulled from the server response so the
      caller can see exactly why it failed.
    - ``SSRF_BLOCKED`` — ``gather_buffer`` raised (URL + no allowlist, or a
      resolved IP in a blocked CIDR). Bubbled through unchanged.
    - Returns ``None`` only for "nothing to upload" cases: ``source`` is
      None, or ``source.kind == "key"`` with an empty ``key``. These are
      caller-constructed inputs, not runtime failures.
    """
    if source is None:
        return None
    if source.kind == "key" and source.key:
        return source.key

    uploader = driver.upload_image if kind == "image" else driver.upload_file
    if uploader is None:
        raise FeishuChannelError(
            FeishuChannelErrorCode.UPLOAD_FAILED,
            f"media uploader missing on driver; cannot send {kind}",
            context={"kind": kind},
        )

    # Propagate an explicit allowlist onto the source, if the caller supplied
    # one AND the source itself does not already set one. This lets the
    # outbound config's default allowlist apply to every URL download.
    if ssrf_allowlist and getattr(source, "_ssrf_allowlist", None) is None:
        try:
            source._ssrf_allowlist = list(ssrf_allowlist)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - frozen dataclass
            pass

    # ``gather_buffer`` raises FeishuChannelError(SSRF_BLOCKED) for URL
    # sources without an allowlist; let that propagate. For buffer / file
    # sources that just fail to read, it still returns (None, default) —
    # we map that to UPLOAD_FAILED so the caller doesn't get "empty body".
    buffer, fname = await gather_buffer(source, default_name=file_name or "upload")
    if buffer is None:
        raise FeishuChannelError(
            FeishuChannelErrorCode.UPLOAD_FAILED,
            f"could not gather bytes for {kind} (source kind={source.kind!r})",
            context={"kind": kind, "source_kind": source.kind},
        )

    kwargs: Dict[str, Any] = {"data": buffer, "file_name": fname}
    if file_type:
        kwargs["file_type"] = file_type
    try:
        raw = await _maybe_await(uploader(**kwargs))
    except FeishuChannelError:
        # Already typed — don't double-wrap.
        raise
    except Exception as e:
        raise FeishuChannelError(
            FeishuChannelErrorCode.UPLOAD_FAILED,
            f"{kind} upload transport error: {e}",
            context={"kind": kind},
        ) from e
    resp = _unwrap(raw)
    if resp.get("code") != 0:
        raw_code = resp.get("code")
        raw_msg = resp.get("msg") or ""
        raise FeishuChannelError(
            FeishuChannelErrorCode.UPLOAD_FAILED,
            f"{kind} upload rejected by server: code={raw_code} msg={raw_msg}",
            context={"kind": kind, "raw_code": raw_code, "raw_msg": raw_msg},
        )
    data = resp.get("data") or {}
    key = data.get("image_key") or data.get("file_key")
    if not key:
        # Response came back with code=0 but no key — malformed server
        # response or mismatched endpoint. Surface instead of swallowing.
        raise FeishuChannelError(
            FeishuChannelErrorCode.UPLOAD_FAILED,
            f"{kind} upload succeeded (code=0) but response missing image_key / file_key",
            context={"kind": kind, "data_keys": list(data.keys())},
        )
    return key


async def gather_buffer(
        source: MediaSource, default_name: str
) -> Tuple[Optional[bytes], str]:
    """Collect a :class:`MediaSource`'s bytes + filename.

    File reads are off-loaded to a worker thread so a large attachment does
    not block the event loop. URL downloads stream with a byte cap to bound
    memory use and hard-require an allowlist to contain SSRF blast radius —
    see the module-level policy note and :func:`.ssrf_guard.assert_public_url`.
    """
    if source.kind == "buffer" and source.buffer is not None:
        return source.buffer, default_name
    if source.kind == "file" and source.path:
        try:
            path_str = source.path
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(
                None, lambda: Path(path_str).read_bytes()
            )
            return data, os.path.basename(path_str) or default_name
        except OSError as e:
            # Preserve the concrete OSError reason (FileNotFoundError,
            # PermissionError, IsADirectoryError, ...) via ``from e`` and
            # surface it as a typed ``UPLOAD_FAILED`` so callers keep the
            # concrete diagnostic instead of seeing a generic send failure.
            raise FeishuChannelError(
                FeishuChannelErrorCode.UPLOAD_FAILED,
                f"could not read local file {source.path!r}: {e}",
                context={"path": source.path, "source_kind": "file"},
            ) from e
    if source.kind == "url" and source.url:
        safe_url = redact_url_for_log(source.url)
        # SSRF guard is mandatory for URL downloads unless an explicit
        # hostname allowlist is provided by the caller. The guard protects
        # against DNS-resolved private / loopback / metadata IPs, but it
        # *cannot* close the TOCTOU window between DNS check and HTTP connect
        # when hostname DNS is attacker-controlled (see ssrf_guard module
        # docstring). An allowlist of trusted hostnames is the only way to
        # make URL uploads safe in hostile-input environments.
        allowlist = getattr(source, "_ssrf_allowlist", None)
        ssrf = getattr(source, "_ssrf_guard", True)
        if not ssrf:
            logger.warning(
                "outbound: SSRF guard explicitly disabled for %s — this is "
                "only safe when the URL is fully trusted",
                safe_url,
            )
        elif not allowlist:
            # No allowlist configured → hard stop. Raise a typed error so
            # the caller sees ``code=SSRF_BLOCKED`` and can surface that to
            # the user; silently returning ``(None, name)`` would be
            # ambiguous with a transient network failure.
            raise FeishuChannelError(
                FeishuChannelErrorCode.SSRF_BLOCKED,
                (
                    f"refusing URL download for {safe_url} — no SSRF "
                    "allowlist configured; set "
                    "OutboundConfig.ssrf_allowlist to trusted hostnames or "
                    "use kind='buffer'/'file' instead"
                ),
                context={"url": safe_url},
            )
        else:
            # Let assert_public_url's FeishuChannelError propagate up as
            # the typed SSRF_BLOCKED error. The earlier swallow-to-None
            # made the block indistinguishable from a download failure.
            await assert_public_url(source.url, allowlist=allowlist)

        cap = int(getattr(source, "_url_download_cap", _URL_DOWNLOAD_DEFAULT_CAP))
        try:
            import httpx  # type: ignore

            async with httpx.AsyncClient(
                    timeout=30, follow_redirects=False
            ) as client:
                async with client.stream("GET", source.url) as r:
                    r.raise_for_status()
                    # Short-circuit when Content-Length already exceeds cap.
                    cl = r.headers.get("content-length")
                    if cl is not None:
                        try:
                            if int(cl) > cap:
                                raise FeishuChannelError(
                                    FeishuChannelErrorCode.UPLOAD_FAILED,
                                    (
                                        f"URL download refused — response "
                                        f"content-length={cl} exceeds cap "
                                        f"({cap} bytes)"
                                    ),
                                    context={
                                        "url": safe_url,
                                        "content_length": cl,
                                        "cap": cap,
                                    },
                                )
                        except ValueError:
                            pass
                    chunks: List[bytes] = []
                    total = 0
                    async for chunk in r.aiter_bytes():
                        total += len(chunk)
                        if total > cap:
                            raise FeishuChannelError(
                                FeishuChannelErrorCode.UPLOAD_FAILED,
                                (
                                    f"URL download exceeded cap mid-stream "
                                    f"({total} > {cap} bytes)"
                                ),
                                context={
                                    "url": safe_url,
                                    "bytes_read": total,
                                    "cap": cap,
                                },
                            )
                        chunks.append(chunk)
                    name = filename_from_url(source.url, default_name)
                    return b"".join(chunks), name
        except FeishuChannelError:
            # Already typed (either our own UPLOAD_FAILED cap violation or a
            # SSRF_BLOCKED from assert_public_url running inside httpx).
            raise
        except Exception as e:
            # Network / TLS / DNS / HTTP-status failures — preserve the
            # concrete exception via ``from e`` instead of losing it.
            raise FeishuChannelError(
                FeishuChannelErrorCode.UPLOAD_FAILED,
                f"URL download of {safe_url} failed: {e}",
                context={"url": safe_url, "source_kind": "url"},
            ) from e
    # Fallthrough: source.kind wasn't one of buffer/file/url, or required
    # attribute missing (e.g. kind="file" with path=None). Caller-constructed
    # input, not a runtime failure — keep the None-None return contract.
    return None, default_name


def filename_from_url(url: str, default: str) -> str:
    try:
        from urllib.parse import urlparse

        p = urlparse(url).path or ""
        base = os.path.basename(p)
        # Defense in depth: strip NUL and any path-traversal artefacts from the
        # attacker-controlled URL path before the name flows into the uploader.
        base = base.replace("\x00", "").replace("/", "").replace("\\", "")
        if len(base) > 255:
            base = base[-255:]
        return base or default
    except Exception:  # pragma: no cover - defensive
        return default


async def _maybe_await(v: Any) -> Any:
    if inspect.isawaitable(v):
        return await v
    return v


def _unwrap(result: Any) -> Dict[str, Any]:
    """Normalize a driver upload response to a plain dict shape."""
    if result is None:
        return {"code": -1, "msg": "empty response"}
    if isinstance(result, dict):
        return result
    code = getattr(result, "code", None)
    if code is None:
        return {"code": -1, "msg": "unknown response"}
    data = getattr(result, "data", None)
    out: Dict[str, Any] = {"code": code, "msg": getattr(result, "msg", "") or ""}
    if data is not None:
        if isinstance(data, dict):
            out["data"] = data
        else:
            try:
                out["data"] = {
                    k: getattr(data, k)
                    for k in dir(data)
                    if not k.startswith("_") and not callable(getattr(data, k))
                }
            except Exception:  # pragma: no cover - defensive
                out["data"] = {}
    return out
