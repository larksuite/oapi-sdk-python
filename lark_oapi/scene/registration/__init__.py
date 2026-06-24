import asyncio
import base64
import gzip
import json
import threading
import time
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

import httpx
import requests

from .errors import AppAccessDeniedError, AppExpiredError, RegisterAppError

_ENDPOINT = "/oauth/v1/app/registration"
_SDK_NAME = "python-sdk"
_AVATAR_MAX_COUNT = 6


def _assert_plain_object(value, path):
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")


def _assert_allowed_keys(obj, allowed_keys, path):
    for key in obj.keys():
        if key not in allowed_keys:
            raise ValueError(f"{path}.{key} is not allowed; allowed keys: {', '.join(allowed_keys)}")


def _validate_string_list(value, path):
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list of strings")

    for index, item in enumerate(value):
        if not isinstance(item, str) or item == "":
            raise ValueError(f"{path}[{index}] must be a non-empty string")

    return value


def _normalize_addons(addons):
    _assert_plain_object(addons, "addons")
    _assert_allowed_keys(addons, ["scopes", "events", "callbacks"], "addons")

    item_count = 0
    normalized = {}

    if "scopes" in addons:
        scopes = addons["scopes"]
        _assert_plain_object(scopes, "addons.scopes")
        _assert_allowed_keys(scopes, ["tenant", "user"], "addons.scopes")

        normalized_scopes = {}
        for key in ("tenant", "user"):
            if key in scopes:
                items = _validate_string_list(scopes[key], f"addons.scopes.{key}")
                item_count += len(items)
                normalized_scopes[key] = items
        normalized["scopes"] = normalized_scopes

    if "events" in addons:
        events = addons["events"]
        _assert_plain_object(events, "addons.events")
        _assert_allowed_keys(events, ["items"], "addons.events")

        if "items" in events:
            event_items = events["items"]
            _assert_plain_object(event_items, "addons.events.items")
            _assert_allowed_keys(event_items, ["tenant", "user"], "addons.events.items")

            normalized_event_items = {}
            for key in ("tenant", "user"):
                if key in event_items:
                    items = _validate_string_list(event_items[key], f"addons.events.items.{key}")
                    item_count += len(items)
                    normalized_event_items[key] = items
            normalized["events"] = {"items": normalized_event_items}

    if "callbacks" in addons:
        callbacks = addons["callbacks"]
        _assert_plain_object(callbacks, "addons.callbacks")
        _assert_allowed_keys(callbacks, ["items"], "addons.callbacks")

        normalized_callbacks = {}
        if "items" in callbacks:
            items = _validate_string_list(callbacks["items"], "addons.callbacks.items")
            item_count += len(items)
            normalized_callbacks["items"] = items
        normalized["callbacks"] = normalized_callbacks

    if item_count == 0:
        raise ValueError("addons must contain at least one scope, event or callback")

    return normalized


def _encode_addons(addons):
    payload = json.dumps(_normalize_addons(addons), ensure_ascii=False, separators=(",", ":"))
    compressed = gzip.compress(payload.encode("utf-8"), mtime=0)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


class _RegistrationFlow:
    def __init__(
            self,
            on_qr_code,
            on_status_change,
            source,
            domain,
            lark_domain,
            app_preset=None,
            addons=None,
            create_only=None,
            app_id=None,
    ):
        if app_id is not None and (not isinstance(app_id, str) or app_id == ""):
            raise ValueError("app_id must be a non-empty string")

        self._on_qr_code = on_qr_code
        self._on_status_change = on_status_change
        self._source = source
        self._base_url = domain
        self._lark_url = lark_domain
        self._app_preset = app_preset
        self._addons = addons
        self._create_only = create_only
        self._app_id = app_id

    def _apply_app_preset(self, params):
        if not self._app_preset:
            return

        avatar = self._app_preset.get("avatar")
        name = self._app_preset.get("name")
        desc = self._app_preset.get("desc")

        if avatar is not None:
            avatars = avatar if isinstance(avatar, list) else [avatar]
            if len(avatars) == 0:
                raise ValueError("app_preset.avatar must contain at least 1 URL")
            if len(avatars) > _AVATAR_MAX_COUNT:
                raise ValueError(
                    f"app_preset.avatar supports at most {_AVATAR_MAX_COUNT} URLs, got {len(avatars)}"
                )
            for index, url in enumerate(avatars):
                if not isinstance(url, str) or url == "":
                    raise ValueError(f"app_preset.avatar[{index}] must be a non-empty string")
            params["avatar"] = avatars

        if name is not None:
            params["name"] = name

        if desc is not None:
            params["desc"] = desc

    def _apply_registration_options(self, params):
        if self._addons is not None:
            params["addons"] = _encode_addons(self._addons)

        if self._create_only is True:
            params["createOnly"] = "true"

        if self._app_id is not None:
            params["clientID"] = self._app_id

    def _build_qr_url(self, uri):
        parsed = urlparse(uri)
        params = parse_qs(parsed.query)
        params["from"] = "sdk"
        params["tp"] = "sdk"
        params["source"] = f"{_SDK_NAME}/{self._source}" if self._source else _SDK_NAME
        # app_preset values only pre-fill the Web app-creation page. Callers
        # pass raw values; urlencode below handles URL encoding automatically.
        self._apply_app_preset(params)
        self._apply_registration_options(params)
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
    def __init__(
            self,
            on_qr_code,
            on_status_change,
            source,
            cancel_event,
            domain,
            lark_domain,
            app_preset=None,
            addons=None,
            create_only=None,
            app_id=None,
    ):
        super().__init__(
            on_qr_code,
            on_status_change,
            source,
            domain,
            lark_domain,
            app_preset=app_preset,
            addons=addons,
            create_only=create_only,
            app_id=app_id,
        )
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
        expire_in = begin_res.get("expires_in", 600)

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
        expire_in = begin_res.get("expires_in", 600)

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
        app_preset=None,
        addons=None,
        create_only=None,
        app_id=None,
):
    flow = _SyncFlow(
        on_qr_code,
        on_status_change,
        source,
        cancel_event,
        domain,
        lark_domain,
        app_preset=app_preset,
        addons=addons,
        create_only=create_only,
        app_id=app_id,
    )
    return flow.run()


async def aregister_app(
        on_qr_code,
        on_status_change=None,
        source=None,
        domain="https://accounts.feishu.cn",
        lark_domain="https://accounts.larksuite.com",
        app_preset=None,
        addons=None,
        create_only=None,
        app_id=None,
):
    flow = _AsyncFlow(
        on_qr_code,
        on_status_change,
        source,
        domain,
        lark_domain,
        app_preset=app_preset,
        addons=addons,
        create_only=create_only,
        app_id=app_id,
    )
    return await flow.run()
