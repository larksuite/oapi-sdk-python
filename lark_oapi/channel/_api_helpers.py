"""Helpers around raw Lark API calls used by :class:`FeishuChannel`.

**Internal module — do not import from outside ``lark_oapi.channel``.** The
leading underscore in the module name is Python's convention for "package
private". Names, signatures, and behaviour here are free to change between
minor versions without deprecation warnings.

Pure async functions taking the underlying ``lark_oapi.Client``. Extracted
from :mod:`.channel` to keep the main class focused on lifecycle and
dispatch; boilerplate around ``contact.v3.user.batch`` / ``im.v1.chat.aget``
lives here instead.
"""

from typing import Any, Dict, List, Optional

from lark_oapi.core.log import logger

from .types import ChatInfo, Identity


async def default_name_lookup(
        lark_client: Any, open_ids: List[str]
) -> Dict[str, Identity]:
    """Resolve open_ids to :class:`Identity` via ``contact.v3.user.batch``.

    Returns ``{}`` on any error so callers degrade gracefully.
    """
    if not open_ids:
        return {}
    try:
        from lark_oapi.api.contact.v3.model.batch_user_request import (
            BatchUserRequest,
        )
    except ImportError:  # pragma: no cover
        return {}
    try:
        req_b = (
            BatchUserRequest.builder()
            .user_id_type("open_id")
            .user_ids(list(open_ids))
        )
        resp = await lark_client.contact.v3.user.abatch(req_b.build())
        data = getattr(resp, "data", None)
        items = getattr(data, "items", None) or []
        out: Dict[str, Identity] = {}
        for item in items:
            oid = getattr(item, "open_id", None)
            if not oid:
                continue
            out[oid] = Identity(
                open_id=oid,
                union_id=getattr(item, "union_id", None),
                user_id=getattr(item, "user_id", None),
                display_name=getattr(item, "name", None)
                             or getattr(item, "en_name", None),
            )
        return out
    except Exception as e:  # pragma: no cover
        logger.debug("default_name_lookup failed: %s", e)
        return {}


async def fetch_chat_info(lark_client: Any, chat_id: str) -> Optional[ChatInfo]:
    """Fetch chat metadata via ``im.v1.chat.aget``. Returns ``None`` on failure.

    Public-API callers expect ``Optional[ChatInfo]``, so failures are logged
    rather than raised. The log always includes ``chat_id`` so operators can
    correlate "this lookup came back empty" with the actual upstream reason
    (403 / 404 / token expired / network).
    """
    try:
        from lark_oapi.api.im.v1.model.get_chat_request import GetChatRequest

        req = GetChatRequest.builder().chat_id(chat_id).build()
        resp = await lark_client.im.v1.chat.aget(req)
        code = getattr(resp, "code", None)
        if code is not None and code != 0:
            logger.warning(
                "fetch_chat_info: chat_id=%s code=%s msg=%s",
                chat_id, code, getattr(resp, "msg", ""),
            )
            return None
        data = getattr(resp, "data", None)
        if data is None:
            return None
        raw_dict: Dict[str, Any] = {}
        for attr in ("name", "description", "chat_type", "owner_id", "user_count"):
            v = getattr(data, attr, None)
            if v is not None:
                raw_dict[attr] = v
        member_count = None
        uc = getattr(data, "user_count", None)
        if uc is not None:
            try:
                member_count = int(uc)
            except (TypeError, ValueError):
                pass
        return ChatInfo(
            chat_id=chat_id,
            name=getattr(data, "name", None),
            description=getattr(data, "description", None),
            chat_type=getattr(data, "chat_type", "unknown") or "unknown",
            owner_id=getattr(data, "owner_id", None),
            member_count=member_count,
            raw=raw_dict,
        )
    except Exception as e:  # pragma: no cover
        logger.warning(
            "fetch_chat_info: chat_id=%s raised: %s", chat_id, e,
        )
        return None


async def fetch_history(
        lark_client: Any,
        *,
        chat_id: str,
        limit: Optional[int] = None,
        before_id: Optional[str] = None,
) -> List[Any]:
    """Fetch recent messages for ``chat_id``.

    ``before_id`` is accepted for source compatibility with earlier internal
    call sites, but the generated list-message builder available here does not
    expose cursoring by message id, so this helper currently ignores it.
    """
    _ = before_id
    try:
        from lark_oapi.api.im.v1.model.list_message_request import ListMessageRequest

        req_b = (
            ListMessageRequest.builder()
            .container_id_type("chat")
            .container_id(chat_id)
        )
        if limit:
            req_b = req_b.page_size(limit)
        resp = await lark_client.im.v1.message.alist(req_b.build())
        data = getattr(resp, "data", None)
        return list(getattr(data, "items", None) or [])
    except Exception as e:  # pragma: no cover
        logger.warning("fetch_history failed: %s", e)
        return []


async def download_media(
        lark_client: Any,
        *,
        message_id: str,
        file_key: str,
        resource_type: str,
) -> Optional[bytes]:
    """Download a message resource (image / file / audio / video attachment).

    Returns the raw bytes, or ``None`` on any failure. The ``None`` contract
    is preserved for back-compat with the public
    :meth:`FeishuChannel.download_resource`; failures are logged with the
    ``message_id`` + ``file_key`` + ``resource_type`` triple so operators
    can pin down which download dropped.
    """
    try:
        # Route by whether the caller supplied a message_id:
        # * With message_id — the key belongs to a message attachment, so the
        #   correct endpoint is `GET /im/v1/messages/:message_id/resources/:file_key`.
        # * Without message_id — the key was minted by a standalone upload
        #   (`POST /im/v1/images` or `POST /im/v1/files`), which is served
        #   by `GET /im/v1/images/:image_key` or `GET /im/v1/files/:file_key`.
        # An empty ``message_id`` against the message-resource endpoint
        # returns 200 with no body, so route to the standalone endpoints in
        # that case.
        if message_id:
            from lark_oapi.api.im.v1.model.get_message_resource_request import (
                GetMessageResourceRequest,
            )
            req = (
                GetMessageResourceRequest.builder()
                .message_id(message_id)
                .file_key(file_key)
                .type(resource_type)
                .build()
            )
            resp = await lark_client.im.v1.message_resource.aget(req)
        elif resource_type == "image":
            from lark_oapi.api.im.v1.model.get_image_request import GetImageRequest
            req = GetImageRequest.builder().image_key(file_key).build()
            resp = await lark_client.im.v1.image.aget(req)
        else:
            from lark_oapi.api.im.v1.model.get_file_request import GetFileRequest
            req = GetFileRequest.builder().file_key(file_key).build()
            resp = await lark_client.im.v1.file.aget(req)

        code = getattr(resp, "code", None)
        if code is not None and code != 0:
            logger.warning(
                "download_media: message_id=%s file_key=%s type=%s "
                "code=%s msg=%s",
                message_id, file_key, resource_type,
                code, getattr(resp, "msg", ""),
            )
            return None
        f = getattr(resp, "file", None)
        if hasattr(f, "read"):
            return f.read()
        if isinstance(f, (bytes, bytearray)):
            return bytes(f)
        logger.warning(
            "download_media: message_id=%s file_key=%s type=%s — "
            "response succeeded but has no file payload",
            message_id, file_key, resource_type,
        )
        return None
    except Exception as e:  # pragma: no cover
        logger.warning(
            "download_media: message_id=%s file_key=%s type=%s raised: %s",
            message_id, file_key, resource_type, e,
        )
        return None


async def download_media_with_meta(
        lark_client: Any,
        *,
        message_id: str,
        file_key: str,
        resource_type: str,
) -> "tuple[Optional[bytes], Optional[str]]":
    """Like :func:`download_media` but also returns a content-type / extension hint.

    The second element of the tuple is one of:

    - the response's ``content_type`` field (preferred, when surfaced);
    - the response's ``file_name`` (used to derive a suffix via mimetypes);
    - ``None`` when nothing is available — the caller falls back to a
      generic suffix.

    Returns ``(None, None)`` on any failure, mirroring ``download_media``'s
    None-on-failure shape.
    """
    try:
        if message_id:
            from lark_oapi.api.im.v1.model.get_message_resource_request import (
                GetMessageResourceRequest,
            )
            req = (
                GetMessageResourceRequest.builder()
                .message_id(message_id)
                .file_key(file_key)
                .type(resource_type)
                .build()
            )
            resp = await lark_client.im.v1.message_resource.aget(req)
        elif resource_type == "image":
            from lark_oapi.api.im.v1.model.get_image_request import GetImageRequest
            req = GetImageRequest.builder().image_key(file_key).build()
            resp = await lark_client.im.v1.image.aget(req)
        else:
            from lark_oapi.api.im.v1.model.get_file_request import GetFileRequest
            req = GetFileRequest.builder().file_key(file_key).build()
            resp = await lark_client.im.v1.file.aget(req)

        code = getattr(resp, "code", None)
        if code is not None and code != 0:
            logger.warning(
                "download_media_with_meta: message_id=%s file_key=%s type=%s "
                "code=%s msg=%s",
                message_id, file_key, resource_type,
                code, getattr(resp, "msg", ""),
            )
            return None, None

        f = getattr(resp, "file", None)
        body: Optional[bytes]
        if hasattr(f, "read"):
            body = f.read()
        elif isinstance(f, (bytes, bytearray)):
            body = bytes(f)
        else:
            body = None

        content_type: Optional[str] = (
                getattr(resp, "content_type", None)
                or getattr(resp, "mime_type", None)
                or getattr(resp, "file_name", None)
        )

        return body, content_type
    except Exception as e:  # pragma: no cover
        logger.warning(
            "download_media_with_meta: message_id=%s file_key=%s type=%s raised: %s",
            message_id, file_key, resource_type, e,
        )
        return None, None


async def mark_read(lark_client: Any, *, message_ids: List[str]) -> Dict[str, Any]:
    try:
        from lark_oapi.api.im.v1.model.read_users_message_request import (
            ReadUsersMessageRequest,
        )
        from lark_oapi.api.im.v1.model.read_users_message_request_body import (
            ReadUsersMessageRequestBody,
        )

        body = (
            ReadUsersMessageRequestBody.builder()
            .message_id_list(message_ids)
            .build()
        )
        req = ReadUsersMessageRequest.builder().request_body(body).build()
        resp = await lark_client.im.v1.message.aread_users(req)
        return {
            "code": getattr(resp, "code", 0),
            "msg": getattr(resp, "msg", "") or "",
        }
    except Exception as e:  # pragma: no cover
        return {"code": -1, "msg": str(e)}
