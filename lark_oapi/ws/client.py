import asyncio
import base64
import http
import inspect
import json
import random
import time
from typing import Callable, Dict, Mapping, Optional
from urllib.parse import urlparse, parse_qs

import requests
import websockets
from websockets.exceptions import InvalidHandshake

from lark_oapi.core.cache import ExpiringCache
from lark_oapi.core.client_assertion import build_proxy_url, extract_aud_from_url
from lark_oapi.core.const import UTF_8, FEISHU_DOMAIN, USER_AGENT, X_TARGET_SERVICE
from lark_oapi.core.enum import LogLevel
from lark_oapi.core.json import JSON
from lark_oapi.core.log import logger
from lark_oapi.core.utils import Strings
from lark_oapi.core.utils.user_agent import build_user_agent
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws.const import *
from lark_oapi.ws.enum import FrameType, MessageType
from lark_oapi.ws.exception import *
from lark_oapi.ws.model import *
from lark_oapi.ws.pb.google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from lark_oapi.ws.pb.pbbp2_pb2 import Frame

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


def _get_by_key(headers: RepeatedCompositeFieldContainer, key: str) -> str:
    for header in headers:
        if header.key == key:
            return header.value

    raise HeaderNotFoundException(key)


def _new_ping_frame(service_id: int) -> Frame:
    frame = Frame()
    header = frame.headers.add()
    header.key = HEADER_TYPE
    header.value = MessageType.PING.value
    frame.service = service_id
    frame.method = FrameType.CONTROL.value
    frame.SeqID = 0
    frame.LogID = 0

    return frame


def _ordinal(n: int):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    if 10 <= n <= 20:
        suffix = 'th'
    else:
        suffix = suffixes.get(n % 10, 'th')
    return str(n) + suffix


async def _select():
    while True:
        await asyncio.sleep(3600)


def _ws_connect_kwargs():
    params = inspect.signature(websockets.connect).parameters
    if "proxy" in params:
        # websockets 15 enables environment proxy discovery by default. The SDK
        # historically connected directly, so preserve that behavior when the
        # parameter exists.
        return {"proxy": None}
    return {}


def _get_ws_conn_exception_headers(e):
    headers = getattr(e, "headers", None)
    if headers is not None:
        return headers

    response = getattr(e, "response", None)
    if response is None:
        return None
    return getattr(response, "headers", None)


def _parse_ws_conn_exception(e):
    headers = _get_ws_conn_exception_headers(e)
    if headers is None:
        raise e

    code = headers.get(HEADER_HANDSHAKE_STATUS)
    msg = headers.get(HEADER_HANDSHAKE_MSG)
    if code is None or msg is None:
        raise e

    code = int(code)
    if code == AUTH_FAILED:
        auth_code = headers.get(HEADER_HANDSHAKE_AUTH_ERRCODE)
        if int(auth_code) == EXCEED_CONN_LIMIT:
            raise ClientException(code, msg)
        else:
            raise ServerException(code, msg)
    elif code == FORBIDDEN:
        raise ClientException(code, msg)
    else:
        raise ServerException(code, msg)


class Client(object):
    def __init__(self,
                 app_id: str,
                 app_secret,
                 log_level: LogLevel = LogLevel.INFO,
                 event_handler: EventDispatcherHandler = None,
                 domain: str = FEISHU_DOMAIN,
                 auto_reconnect: bool = True,
                 source: Optional[str] = None,
                 extra_ua_tags: Optional[list] = None,
                 headers: Optional[Mapping[str, str]] = None,
                 client_assertion_provider=None) -> None:
        self._app_id: str = app_id
        self._app_secret: str = app_secret
        self._log_level: LogLevel = log_level
        self._event_handler: EventDispatcherHandler = event_handler
        self._auto_reconnect: bool = auto_reconnect
        self._domain: str = domain
        self._client_assertion_provider = client_assertion_provider
        self._headers: Dict[str, str] = dict(headers or {})
        # UA used on the endpoint-discovery POST (and any future HTTP/WS
        # handshakes from this client). ``extra_ua_tags`` is internal — sub-
        # modules (e.g. FeishuChannel) pass ``["channel"]`` here.
        self._user_agent: str = build_user_agent(source=source, extra_tags=extra_ua_tags)
        self._conn: Optional[websockets.WebSocketClientProtocol] = None
        self._conn_url: str = ""
        self._service_id: str = ""
        self._conn_id: str = ""
        # Local defaults; the Feishu WS endpoint authoritatively replaces these
        # via _configure() on every handshake (and may push updates mid-session
        # via CONTROL frames). Matches node-sdk parent SDK — user-facing
        # overrides are intentionally not exposed.
        self._reconnect_nonce: int = 30
        self._reconnect_count: int = -1
        self._reconnect_interval: int = 120
        self._ping_interval: int = 120
        self._cache: ExpiringCache = ExpiringCache(clear_interval=30)
        self._lock = asyncio.Lock()
        # Observer hooks for higher-level wrappers (e.g. FeishuChannel) to
        # react to reconnect lifecycle. ``on_reconnecting`` fires when the
        # client decides a connection was lost and starts retrying;
        # ``on_reconnected`` fires on the first successful re-establishment.
        # Both default to no-op so existing callers see no behaviour change.
        self.on_reconnecting: Callable[[], None] = lambda: None
        self.on_reconnected: Callable[[], None] = lambda: None
        logger.setLevel(log_level.value)

    def start(self) -> None:
        try:
            loop.run_until_complete(self._connect())
        except ClientException as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            raise e
        except Exception as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            loop.run_until_complete(self._disconnect())
            if self._auto_reconnect:
                loop.run_until_complete(self._reconnect())
            else:
                raise e

        loop.create_task(self._ping_loop())
        loop.run_until_complete(_select())

    async def _ping_loop(self):
        while True:
            try:
                if self._conn is not None:
                    frame = _new_ping_frame(int(self._service_id))
                    await self._write_message(frame.SerializeToString())
                    logger.debug(self._fmt_log("ping success"))
            except Exception as e:
                logger.warn(self._fmt_log("ping failed, err: {}", e))
            finally:
                await asyncio.sleep(self._ping_interval)

    async def _connect(self) -> None:
        await self._lock.acquire()
        if self._conn is not None:
            return
        try:
            conn_url = self._get_conn_url()
            u = urlparse(conn_url)
            q = parse_qs(u.query)
            conn_id = q[DEVICE_ID][0]
            service_id = q[SERVICE_ID][0]

            conn = await websockets.connect(conn_url, **_ws_connect_kwargs())
            self._conn = conn
            self._conn_url = conn_url
            self._conn_id = conn_id
            self._service_id = service_id

            logger.info(self._fmt_log("connected to {}", conn_url))
            loop.create_task(self._receive_message_loop())
        except InvalidHandshake as e:
            _parse_ws_conn_exception(e)
        finally:
            self._lock.release()

    async def _receive_message_loop(self):
        try:
            while True:
                if self._conn is None:
                    raise ConnectionClosedException("connection is closed")
                msg = await self._conn.recv()
                loop.create_task(self._handle_message(msg))
        except Exception as e:
            logger.error(self._fmt_log("receive message loop exit, err: {}", e))
            await self._disconnect()
            if self._auto_reconnect:
                await self._reconnect()
            else:
                raise e

    def _get_conn_url(self) -> str:
        if Strings.is_empty(self._app_id) or (
                self._client_assertion_provider is None and Strings.is_empty(self._app_secret)
        ):
            raise ClientException(
                NO_CREDENTIAL,
                "app_id is required and either app_secret or client_assertion_provider is required",
            )

        headers = dict(self._headers)
        headers.update({
            "locale": "zh",
            USER_AGENT: self._user_agent,
        })
        url = self._domain + GEN_ENDPOINT_URI
        body = {"AppID": self._app_id}
        if self._client_assertion_provider is not None:
            aud = extract_aud_from_url(self._domain)
            assertion_token = self._client_assertion_provider.retrieve_token(aud)
            if assertion_token is None or Strings.is_empty(assertion_token.value):
                raise ClientException(7101, "client assertion token is empty")
            body["AppSecret"] = ""
            body["ClientAssertion"] = assertion_token.value
            if assertion_token.target_info is not None:
                url = build_proxy_url(assertion_token.target_info, GEN_ENDPOINT_URI)
                headers[X_TARGET_SERVICE] = aud
        else:
            body["AppSecret"] = self._app_secret

        response = requests.post(
            url,
            headers=headers,
            json=body,
        )
        if response.status_code != http.HTTPStatus.OK:
            msg = "system busy"
            try:
                payload = json.loads(str(response.content, UTF_8))
                msg = payload.get("msg") or msg
            except Exception:
                pass
            raise ServerException(response.status_code, msg)

        resp = JSON.unmarshal(str(response.content, UTF_8), EndpointResp)
        if resp.code == OK:
            pass
        elif resp.code == SYSTEM_BUSY:
            raise ServerException(resp.code, "system busy")
        elif resp.code == INTERNAL_ERROR:
            raise ServerException(resp.code, resp.msg)
        else:
            raise ClientException(resp.code, resp.msg)

        data = resp.data
        if data.ClientConfig is not None:
            self._configure(data.ClientConfig)

        return data.URL

    async def _handle_message(self, msg: bytes) -> None:
        try:
            frame = Frame()
            frame.ParseFromString(msg)
            ft = FrameType(frame.method)

            if ft == FrameType.CONTROL:
                await self._handle_control_frame(frame)
            elif ft == FrameType.DATA:
                await self._handle_data_frame(frame)
        except Exception as e:
            logger.error(self._fmt_log("handle message failed, err: {}", e))

    async def _handle_control_frame(self, frame: Frame):
        hs = frame.headers
        type_ = _get_by_key(hs, HEADER_TYPE)
        message_type = MessageType(type_)

        if message_type == MessageType.PING:
            return
        elif message_type == MessageType.PONG:
            logger.debug(self._fmt_log("receive pong"))
            if not frame.payload:
                return
            conf = JSON.unmarshal(str(frame.payload, UTF_8), ClientConfig)
            self._configure(conf)

    async def _handle_data_frame(self, frame: Frame):
        hs = frame.headers
        msg_id = _get_by_key(hs, HEADER_MESSAGE_ID)
        trace_id = _get_by_key(hs, HEADER_TRACE_ID)
        sum_ = _get_by_key(hs, HEADER_SUM)
        seq = _get_by_key(hs, HEADER_SEQ)
        type_ = _get_by_key(hs, HEADER_TYPE)

        pl = frame.payload
        if int(sum_) > 1:
            # 合包
            pl = self._combine(msg_id, int(sum_), int(seq), pl)
            if pl is None:
                return

        message_type = MessageType(type_)
        logger.debug(self._fmt_log("receive message, message_type: {}, message_id: {}, trace_id: {}, payload: {}",
                                   message_type.value, msg_id, trace_id, pl.decode(UTF_8)))

        resp = Response(code=http.HTTPStatus.OK)
        try:
            start = int(round(time.time() * 1000))
            if message_type == MessageType.EVENT:
                result = self._event_handler._do_without_validation(pl)
            elif message_type == MessageType.CARD:
                return
            else:
                return
            end = int(round(time.time() * 1000))
            header = hs.add()
            header.key = HEADER_BIZ_RT
            header.value = str(end - start)
            if result is not None:
                resp.data = base64.b64encode(JSON.marshal(result).encode(UTF_8))
        except Exception as e:
            logger.error(
                self._fmt_log("handle message failed, message_type: {}, message_id: {}, trace_id: {}, err: {}",
                              message_type.value, msg_id, trace_id, e))
            resp = Response(code=http.HTTPStatus.INTERNAL_SERVER_ERROR)

        frame.payload = JSON.marshal(resp).encode(UTF_8)
        await self._write_message(frame.SerializeToString())

    async def _reconnect(self):
        # Notify subscribers that we're about to try reconnecting. Wrapped in
        # try/except so a misbehaving observer can never derail reconnect.
        try:
            self.on_reconnecting()
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(self._fmt_log("on_reconnecting callback raised: {}", e))

        # 首次重连随机抖动
        if self._reconnect_nonce > 0:
            nonce = random.random() * self._reconnect_nonce
            await asyncio.sleep(nonce)

        # 重连
        if self._reconnect_count >= 0:
            for i in range(self._reconnect_count):
                if await self._try_connect(i):
                    self._fire_on_reconnected()
                    return
                await asyncio.sleep(self._reconnect_interval)
            raise ServerUnreachableException(
                f"unable to connect to the server after trying {self._reconnect_count} times")
        else:
            i = 0
            while True:
                if await self._try_connect(i):
                    self._fire_on_reconnected()
                    return
                await asyncio.sleep(self._reconnect_interval)
                i += 1

    def _fire_on_reconnected(self) -> None:
        try:
            self.on_reconnected()
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(self._fmt_log("on_reconnected callback raised: {}", e))

    async def _try_connect(self, cnt: int) -> bool:
        logger.info(self._fmt_log("trying to reconnect for the {} time", _ordinal(cnt + 1)))
        try:
            await self._connect()
            return True
        except ClientException as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            raise e
        except Exception as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            return False

    async def _disconnect(self):
        try:
            await self._lock.acquire()
            if self._conn is None:
                return
            await self._conn.close()
            logger.info(self._fmt_log("disconnected to {}", self._conn_url))
        finally:
            self._conn = None
            self._conn_url = ""
            self._conn_id = ""
            self._service_id = ""
            self._lock.release()

    async def _write_message(self, data: bytes):
        async with self._lock:
            if self._conn is None:
                raise ConnectionClosedException("connection is closed, write message failed")
            await self._conn.send(data)

    def _combine(self, msg_id: str, sum_: int, seq: int, bs: bytes) -> Optional[bytes]:
        val = self._cache.get(msg_id)
        if val is None:
            buf = [b''] * sum_
            buf[seq] = bs
            self._cache.set(msg_id, buf, 5)
            return None

        val[seq] = bs
        pl = b''
        for v in val:
            if not v:
                self._cache.set(msg_id, val, 5)
                return None
            pl += v

        return pl

    def _configure(self, conf: ClientConfig) -> None:
        self._reconnect_count = conf.ReconnectCount
        self._reconnect_interval = conf.ReconnectInterval
        self._reconnect_nonce = conf.ReconnectNonce
        self._ping_interval = conf.PingInterval

    def _fmt_log(self, fmt: str, *args) -> str:
        log = fmt.format(*args)
        if self._conn_id != "":
            log += f' [conn_id={self._conn_id}]'

        return log
