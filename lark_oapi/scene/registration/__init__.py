import asyncio
import threading
import time
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

import httpx
import requests

from .errors import AppAccessDeniedError, AppExpiredError, RegisterAppError

_ENDPOINT = "/oauth/v1/app/registration"
_SDK_NAME = "python-sdk"


class _RegistrationFlow:
    def __init__(self, on_qr_code, on_status_change, source, domain, lark_domain):
        self._on_qr_code = on_qr_code
        self._on_status_change = on_status_change
        self._source = source
        self._base_url = domain
        self._lark_url = lark_domain

    def _build_qr_url(self, uri):
        parsed = urlparse(uri)
        params = parse_qs(parsed.query)
        params["from"] = "sdk"
        params["tp"] = "sdk"
        params["source"] = f"{_SDK_NAME}/{self._source}" if self._source else _SDK_NAME
        return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

    def _notify_status(self, status, interval=None):
        if self._on_status_change is None:
            return
        info = {"status": status}
        if interval is not None:
            info["interval"] = interval
        self._on_status_change(info)

    def _handle_poll_response(self, data, domain_switched):
        # success
        if data.get("client_id") and data.get("client_secret"):
            result = {
                "client_id": data["client_id"],
                "client_secret": data["client_secret"],
            }
            if data.get("user_info"):
                result["user_info"] = data["user_info"]
            return "success", result

        # domain switch
        user_info = data.get("user_info") or {}
        if user_info.get("tenant_brand") == "lark" and not domain_switched:
            self._base_url = self._lark_url
            self._notify_status("domain_switched")
            return "domain_switched", None

        error = data.get("error", "")
        error_desc = data.get("error_description", "")

        if error == "authorization_pending":
            self._notify_status("polling")
            return "pending", None

        if error == "slow_down":
            return "slow_down", None

        if error == "access_denied":
            raise AppAccessDeniedError(error, error_desc)

        if error == "expired_token":
            raise AppExpiredError(error, error_desc)

        raise RegisterAppError(error, error_desc)


class _SyncFlow(_RegistrationFlow):
    def __init__(self, on_qr_code, on_status_change, source, cancel_event, domain, lark_domain):
        super().__init__(on_qr_code, on_status_change, source, domain, lark_domain)
        self._cancel_event = cancel_event

    def _post(self, data):
        resp = requests.post(
            self._base_url + _ENDPOINT,
            data=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return resp.json()

    def _check_cancelled(self):
        if self._cancel_event is not None and self._cancel_event.is_set():
            raise RegisterAppError("abort", "cancelled by caller")

    def run(self):
        self._check_cancelled()

        # init
        init_res = self._post({"action": "init"})
        methods = init_res.get("supported_auth_methods") or []
        if "client_secret" not in methods:
            raise RegisterAppError(
                "unsupported_auth_method",
                "client_secret not in supported_auth_methods",
            )

        # begin
        begin_res = self._post({
            "action": "begin",
            "archetype": "PersonalAgent",
            "auth_method": "client_secret",
            "request_user_info": "open_id",
        })

        device_code = begin_res["device_code"]
        interval = begin_res.get("interval", 5)
        expire_in = begin_res.get("expire_in", 600)

        qr_url = self._build_qr_url(begin_res["verification_uri_complete"])
        self._on_qr_code({"url": qr_url, "expire_in": expire_in})

        # poll
        deadline = time.monotonic() + expire_in
        domain_switched = False

        while time.monotonic() < deadline:
            self._check_cancelled()

            poll_res = self._post({"action": "poll", "device_code": device_code})

            action, result = self._handle_poll_response(poll_res, domain_switched)

            if action == "success":
                return result

            if action == "domain_switched":
                domain_switched = True
                continue

            if action == "slow_down":
                interval += 5
                self._notify_status("slow_down", interval)

            time.sleep(interval)

        raise AppExpiredError("expired_token", "polling timed out")


class _AsyncFlow(_RegistrationFlow):
    async def _post(self, data):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self._base_url + _ENDPOINT,
                content=urlencode(data),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            return resp.json()

    async def run(self):
        # init
        init_res = await self._post({"action": "init"})
        methods = init_res.get("supported_auth_methods") or []
        if "client_secret" not in methods:
            raise RegisterAppError(
                "unsupported_auth_method",
                "client_secret not in supported_auth_methods",
            )

        # begin
        begin_res = await self._post({
            "action": "begin",
            "archetype": "PersonalAgent",
            "auth_method": "client_secret",
            "request_user_info": "open_id",
        })

        device_code = begin_res["device_code"]
        interval = begin_res.get("interval", 5)
        expire_in = begin_res.get("expire_in", 600)

        qr_url = self._build_qr_url(begin_res["verification_uri_complete"])
        self._on_qr_code({"url": qr_url, "expire_in": expire_in})

        # poll
        deadline = time.monotonic() + expire_in
        domain_switched = False

        while time.monotonic() < deadline:
            poll_res = await self._post({"action": "poll", "device_code": device_code})

            action, result = self._handle_poll_response(poll_res, domain_switched)

            if action == "success":
                return result

            if action == "domain_switched":
                domain_switched = True
                continue

            if action == "slow_down":
                interval += 5
                self._notify_status("slow_down", interval)

            await asyncio.sleep(interval)

        raise AppExpiredError("expired_token", "polling timed out")


def register_app(
    on_qr_code,
    on_status_change=None,
    source=None,
    cancel_event=None,
    domain="https://accounts.feishu.cn",
    lark_domain="https://accounts.larksuite.com",
):
    flow = _SyncFlow(on_qr_code, on_status_change, source, cancel_event, domain, lark_domain)
    return flow.run()


async def aregister_app(
    on_qr_code,
    on_status_change=None,
    source=None,
    domain="https://accounts.feishu.cn",
    lark_domain="https://accounts.larksuite.com",
):
    flow = _AsyncFlow(on_qr_code, on_status_change, source, domain, lark_domain)
    return await flow.run()
