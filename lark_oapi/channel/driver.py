"""Bridge between the channel layer and the underlying `lark_oapi.Client`.

Rather than coupling the channel to specific Request/Response types of the
generated API surface, we adapt them here into plain dict calls that the
OutboundSender / pipeline expect. This also makes it trivial to mock the
driver in tests.
"""

import io
import json
from typing import Any, Dict, Optional

from lark_oapi.api.im.v1.model.create_message_request import CreateMessageRequest
from lark_oapi.api.im.v1.model.create_message_request_body import CreateMessageRequestBody
from lark_oapi.api.im.v1.model.create_message_reaction_request import CreateMessageReactionRequest
from lark_oapi.api.im.v1.model.create_message_reaction_request_body import CreateMessageReactionRequestBody
from lark_oapi.api.im.v1.model.delete_message_reaction_request import DeleteMessageReactionRequest
from lark_oapi.api.im.v1.model.delete_message_request import DeleteMessageRequest
from lark_oapi.api.im.v1.model.forward_message_request import ForwardMessageRequest
from lark_oapi.api.im.v1.model.forward_message_request_body import ForwardMessageRequestBody
from lark_oapi.api.im.v1.model.get_message_request import GetMessageRequest
from lark_oapi.api.im.v1.model.patch_message_request import PatchMessageRequest
from lark_oapi.api.im.v1.model.patch_message_request_body import PatchMessageRequestBody
from lark_oapi.api.im.v1.model.reply_message_request import ReplyMessageRequest
from lark_oapi.api.im.v1.model.reply_message_request_body import ReplyMessageRequestBody
from lark_oapi.api.im.v1.model.update_message_request import UpdateMessageRequest
from lark_oapi.api.im.v1.model.update_message_request_body import UpdateMessageRequestBody
from lark_oapi.api.im.v1.model.emoji import Emoji
from lark_oapi.client import Client
from lark_oapi.core.json import JSON

from .outbound.sender import SendDriver


def _as_upload_stream(data: bytes, name: str) -> io.BytesIO:
    bio = io.BytesIO(data)
    bio.name = name
    return bio


def _resp_to_dict(resp: Any) -> Dict[str, Any]:
    code = getattr(resp, "code", None)
    msg = getattr(resp, "msg", None)
    data_obj = getattr(resp, "data", None)
    out: Dict[str, Any] = {"code": code if code is not None else 0, "msg": msg or ""}
    if data_obj is not None:
        try:
            # Use the SDK's JSON marshaller for consistent dict shape.
            out["data"] = json.loads(JSON.marshal(data_obj))
        except Exception:
            # Best-effort: shallow copy of attrs.
            out["data"] = {
                k: getattr(data_obj, k)
                for k in dir(data_obj)
                if not k.startswith("_") and not callable(getattr(data_obj, k, None))
            }
    return out


class LarkClientDriver:
    """Adapt a `lark_oapi.Client` instance into the driver methods we need."""

    def __init__(self, client: Client) -> None:
        self._client = client

    # -------- send ------------------------------------------------------------
    async def create_message(
            self,
            *,
            receive_id_type: str,
            receive_id: str,
            msg_type: str,
            content: str,
            uuid: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = (
            CreateMessageRequestBody.builder()
            .receive_id(receive_id)
            .msg_type(msg_type)
            .content(content)
        )
        if uuid:
            body = body.uuid(uuid)
        req = (
            CreateMessageRequest.builder()
            .receive_id_type(receive_id_type)
            .request_body(body.build())
            .build()
        )
        resp = await self._client.im.v1.message.acreate(req)
        return _resp_to_dict(resp)

    async def reply_message(
            self,
            *,
            message_id: str,
            msg_type: str,
            content: str,
            uuid: Optional[str] = None,
            reply_in_thread: Optional[bool] = None,
    ) -> Dict[str, Any]:
        body = ReplyMessageRequestBody.builder().content(content).msg_type(msg_type)
        if reply_in_thread is not None:
            body = body.reply_in_thread(reply_in_thread)
        if uuid:
            body = body.uuid(uuid)
        req = (
            ReplyMessageRequest.builder()
            .message_id(message_id)
            .request_body(body.build())
            .build()
        )
        resp = await self._client.im.v1.message.areply(req)
        return _resp_to_dict(resp)

    async def patch_message(
            self,
            *,
            message_id: str,
            content: str,
    ) -> Dict[str, Any]:
        req = (
            PatchMessageRequest.builder()
            .message_id(message_id)
            .request_body(PatchMessageRequestBody.builder().content(content).build())
            .build()
        )
        resp = await self._client.im.v1.message.apatch(req)
        return _resp_to_dict(resp)

    async def update_message(
            self,
            *,
            message_id: str,
            msg_type: str,
            content: str,
    ) -> Dict[str, Any]:
        body = (
            UpdateMessageRequestBody.builder()
            .msg_type(msg_type)
            .content(content)
            .build()
        )
        req = (
            UpdateMessageRequest.builder()
            .message_id(message_id)
            .request_body(body)
            .build()
        )
        resp = await self._client.im.v1.message.aupdate(req)
        return _resp_to_dict(resp)

    async def delete_message(self, *, message_id: str) -> Dict[str, Any]:
        req = DeleteMessageRequest.builder().message_id(message_id).build()
        resp = await self._client.im.v1.message.adelete(req)
        return _resp_to_dict(resp)

    async def forward_message(
            self,
            *,
            message_id: str,
            chat_id: str,
    ) -> Dict[str, Any]:
        body = ForwardMessageRequestBody.builder().receive_id(chat_id).build()
        req = (
            ForwardMessageRequest.builder()
            .message_id(message_id)
            .receive_id_type("chat_id")
            .request_body(body)
            .build()
        )
        resp = await self._client.im.v1.message.aforward(req)
        return _resp_to_dict(resp)

    async def fetch_message(self, message_id: str) -> Dict[str, Any]:
        req = GetMessageRequest.builder().message_id(message_id).build()
        resp = await self._client.im.v1.message.aget(req)
        return _resp_to_dict(resp)

    async def add_reaction(self, *, message_id: str, emoji_type: str) -> Dict[str, Any]:
        body = (
            CreateMessageReactionRequestBody.builder()
            .reaction_type(Emoji.builder().emoji_type(emoji_type).build())
            .build()
        )
        req = (
            CreateMessageReactionRequest.builder()
            .message_id(message_id)
            .request_body(body)
            .build()
        )
        resp = await self._client.im.v1.message_reaction.acreate(req)
        return _resp_to_dict(resp)

    async def remove_reaction(self, *, message_id: str, reaction_id: str) -> Dict[str, Any]:
        req = (
            DeleteMessageReactionRequest.builder()
            .message_id(message_id)
            .reaction_id(reaction_id)
            .build()
        )
        resp = await self._client.im.v1.message_reaction.adelete(req)
        return _resp_to_dict(resp)

    # -------- media upload ----------------------------------------------------
    async def upload_image(self, *, data: bytes, file_name: str = "") -> Dict[str, Any]:
        try:
            from lark_oapi.api.im.v1.model.create_image_request import CreateImageRequest
            from lark_oapi.api.im.v1.model.create_image_request_body import CreateImageRequestBody
        except ImportError:  # pragma: no cover
            return {"code": -1, "msg": "image upload model missing"}
        # The SDK's multipart serializer (`Files.extract_files`) only picks up
        # fields whose value is an `io.IOBase`; raw `bytes` are silently
        # dropped, which makes the server reject the request as 234001
        # "Invalid request param". Wrap the buffer in a BytesIO and attach a
        # filename so the multipart part is well-formed.
        body = (
            CreateImageRequestBody.builder()
            .image_type("message")
            .image(_as_upload_stream(data, file_name or "image"))
            .build()
        )
        req = CreateImageRequest.builder().request_body(body).build()
        resp = await self._client.im.v1.image.acreate(req)
        return _resp_to_dict(resp)

    async def upload_file(
            self,
            *,
            data: bytes,
            file_name: str = "",
            file_type: str = "stream",
    ) -> Dict[str, Any]:
        try:
            from lark_oapi.api.im.v1.model.create_file_request import CreateFileRequest
            from lark_oapi.api.im.v1.model.create_file_request_body import CreateFileRequestBody
        except ImportError:  # pragma: no cover
            return {"code": -1, "msg": "file upload model missing"}
        name = file_name or "upload"
        body = (
            CreateFileRequestBody.builder()
            .file_type(file_type)
            .file_name(name)
            .file(_as_upload_stream(data, name))
            .build()
        )
        req = CreateFileRequest.builder().request_body(body).build()
        resp = await self._client.im.v1.file.acreate(req)
        return _resp_to_dict(resp)

    # -------- cardkit preallocation (node-aligned) ----------------------------
    async def cardkit_create(self, *, body: Dict[str, Any]) -> Dict[str, Any]:
        """POST ``/open-apis/cardkit/v1/card``. ``body`` is ``{type, data}``."""
        from lark_oapi.api.cardkit.v1.model.create_card_request import CreateCardRequest
        from lark_oapi.api.cardkit.v1.model.create_card_request_body import (
            CreateCardRequestBody,
        )

        rb = (
            CreateCardRequestBody.builder()
            .type(body.get("type") or "card_json")
            .data(body.get("data") or "")
            .build()
        )
        req = CreateCardRequest.builder().request_body(rb).build()
        resp = await self._client.cardkit.v1.card.acreate(req)
        return _resp_to_dict(resp)

    async def cardkit_update_element(
            self, *, card_id: str, element_id: str, body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """POST ``/open-apis/cardkit/v1/card/{card_id}/element/{element_id}/content``."""
        from lark_oapi.api.cardkit.v1.model.content_card_element_request import (
            ContentCardElementRequest,
        )
        from lark_oapi.api.cardkit.v1.model.content_card_element_request_body import (
            ContentCardElementRequestBody,
        )

        rb_b = ContentCardElementRequestBody.builder().content(
            body.get("content") or ""
        )
        seq = body.get("sequence")
        if seq is not None:
            rb_b = rb_b.sequence(int(seq))
        req = (
            ContentCardElementRequest.builder()
            .card_id(card_id)
            .element_id(element_id)
            .request_body(rb_b.build())
            .build()
        )
        resp = await self._client.cardkit.v1.card_element.acontent(req)
        return _resp_to_dict(resp)

    async def cardkit_update_settings(
            self, *, card_id: str, body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """POST ``/open-apis/cardkit/v1/card/{card_id}/settings``."""
        from lark_oapi.api.cardkit.v1.model.settings_card_request import (
            SettingsCardRequest,
        )
        from lark_oapi.api.cardkit.v1.model.settings_card_request_body import (
            SettingsCardRequestBody,
        )

        rb_b = SettingsCardRequestBody.builder().settings(body.get("settings") or "")
        seq = body.get("sequence")
        if seq is not None:
            rb_b = rb_b.sequence(int(seq))
        req = (
            SettingsCardRequest.builder()
            .card_id(card_id)
            .request_body(rb_b.build())
            .build()
        )
        resp = await self._client.cardkit.v1.card.asettings(req)
        return _resp_to_dict(resp)

    # -------- public helpers --------------------------------------------------
    def send_driver(self) -> SendDriver:
        return SendDriver(
            create_message=self.create_message,
            reply_message=self.reply_message,
            patch_message=self.patch_message,
            delete_message=self.delete_message,
            forward_message=self.forward_message,
            upload_image=self.upload_image,
            upload_file=self.upload_file,
        )
