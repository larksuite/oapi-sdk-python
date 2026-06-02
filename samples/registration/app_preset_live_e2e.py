#!/usr/bin/env python3
"""Manual live E2E for one-click app registration app_preset.

This script does not mock registration responses. It calls the real accounts
registration endpoint, prints the QR/verification URL, waits for a user to scan
and submit the app-creation page, then verifies that credentials are returned.

Example:
    python3 samples/registration/app_preset_live_e2e.py --open

Optional environment overrides:
    LARK_REGISTRATION_DOMAIN=https://accounts.feishu.cn
    LARK_REGISTRATION_LARK_DOMAIN=https://accounts.larksuite.com
    LARK_REGISTRATION_SOURCE=python-live-e2e
    LARK_REGISTRATION_NAME="{user}'s app"
    LARK_REGISTRATION_DESC="Created by Python SDK live E2E"
    LARK_REGISTRATION_AVATARS="https://s1-imfile.feishucdn.com/static-resource/v1/v3_00cj_d6bebede-c56b-40a2-b767-8e9da07f3b3g,https://s1-imfile.feishucdn.com/static-resource/v1/v2_bc5d2075-fcbd-41f8-bfe3-5a5ecbf0f7dg"
"""

import argparse
import os
import sys
import webbrowser
from urllib.parse import parse_qs, urlparse

import requests

import lark_oapi as lark
from lark_oapi.scene.registration import RegisterAppError

DEFAULT_AVATARS = [
    "https://s1-imfile.feishucdn.com/static-resource/v1/v3_00cj_d6bebede-c56b-40a2-b767-8e9da07f3b3g",
    "https://s1-imfile.feishucdn.com/static-resource/v1/v2_bc5d2075-fcbd-41f8-bfe3-5a5ecbf0f7dg",
]


def _csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _mask_secret(value):
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Run a real one-click app registration flow with app_preset.",
    )
    parser.add_argument(
        "--domain",
        default=os.getenv("LARK_REGISTRATION_DOMAIN", "https://accounts.feishu.cn"),
        help="Accounts base URL for Feishu.",
    )
    parser.add_argument(
        "--lark-domain",
        default=os.getenv("LARK_REGISTRATION_LARK_DOMAIN", "https://accounts.larksuite.com"),
        help="Accounts base URL used after tenant_brand=lark domain switch.",
    )
    parser.add_argument(
        "--source",
        default=os.getenv("LARK_REGISTRATION_SOURCE", "python-live-e2e"),
        help="Source suffix appended as python-sdk/{source}.",
    )
    parser.add_argument(
        "--name",
        default=os.getenv("LARK_REGISTRATION_NAME", "{user}'s Python SDK app"),
        help="Raw app name pre-fill value. Do not URL-encode it.",
    )
    parser.add_argument(
        "--desc",
        default=os.getenv("LARK_REGISTRATION_DESC", "Created by Python SDK live E2E"),
        help="Raw app description pre-fill value. Do not URL-encode it.",
    )
    parser.add_argument(
        "--avatar",
        action="append",
        dest="avatars",
        help="Public image URL for avatar pre-fill. Repeat for multiple avatars.",
    )
    parser.add_argument(
        "--no-avatar",
        action="store_true",
        help="Do not send avatar in app_preset.",
    )
    parser.add_argument(
        "--skip-avatar-check",
        action="store_true",
        help="Skip best-effort HTTP HEAD checks for avatar URLs.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the verification URL in the default browser.",
    )
    return parser


def _build_app_preset(args):
    app_preset = {
        "name": args.name,
        "desc": args.desc,
    }
    if not args.no_avatar:
        env_avatars = _csv(os.getenv("LARK_REGISTRATION_AVATARS", ""))
        app_preset["avatar"] = args.avatars or env_avatars or DEFAULT_AVATARS
    return app_preset


def _check_avatar_urls(avatars):
    for avatar in avatars:
        try:
            response = requests.head(avatar, allow_redirects=True, timeout=5)
        except requests.RequestException as err:
            print(f"[warn] avatar HEAD check failed: {avatar} ({err})")
            continue
        content_type = response.headers.get("content-type", "")
        if response.status_code >= 400:
            print(f"[warn] avatar may be unavailable: {avatar} status={response.status_code}")
        elif content_type and not content_type.startswith("image/"):
            print(f"[warn] avatar may not be an image: {avatar} content-type={content_type}")


def _assert_qr_url_contains_preset(url, app_preset):
    query = parse_qs(urlparse(url).query)
    expected_avatars = app_preset.get("avatar")
    if isinstance(expected_avatars, str):
        expected_avatars = [expected_avatars]
    if expected_avatars is not None and query.get("avatar") != expected_avatars:
        raise AssertionError(f"avatar query mismatch: expected {expected_avatars}, got {query.get('avatar')}")
    if app_preset.get("name") is not None and query.get("name") != [app_preset["name"]]:
        raise AssertionError(f"name query mismatch: expected {app_preset['name']}, got {query.get('name')}")
    if app_preset.get("desc") is not None and query.get("desc") != [app_preset["desc"]]:
        raise AssertionError(f"desc query mismatch: expected {app_preset['desc']}, got {query.get('desc')}")


def main():
    args = _build_parser().parse_args()
    app_preset = _build_app_preset(args)
    avatars = app_preset.get("avatar")

    print("[live-e2e] Starting real one-click app registration.")
    print("[live-e2e] app_preset raw values:")
    print(f"  name: {app_preset.get('name')}")
    print(f"  desc: {app_preset.get('desc')}")
    print(f"  avatar: {avatars if avatars is not None else '<not sent>'}")
    print()

    if avatars is not None and not args.skip_avatar_check:
        _check_avatar_urls(avatars if isinstance(avatars, list) else [avatars])

    def on_qr_code(info):
        url = info["url"]
        _assert_qr_url_contains_preset(url, app_preset)
        print("[live-e2e] Verification URL is ready.")
        print(f"  expire_in: {info.get('expire_in')}")
        print(f"  url: {url}")
        print()
        print("[live-e2e] Open the URL, scan/sign in, inspect pre-filled fields, then submit the page.")
        if args.open:
            webbrowser.open(url)

    def on_status_change(info):
        print(f"[live-e2e] status: {info}")

    try:
        result = lark.register_app(
            on_qr_code=on_qr_code,
            on_status_change=on_status_change,
            source=args.source,
            domain=args.domain,
            lark_domain=args.lark_domain,
            app_preset=app_preset,
        )
    except RegisterAppError as err:
        print(f"[live-e2e] registration failed: {err.code}: {err.description}", file=sys.stderr)
        return 1

    client_id = result.get("client_id")
    client_secret = result.get("client_secret")
    user_info = result.get("user_info")
    if not client_id or not client_secret:
        print(f"[live-e2e] missing credentials in result: {result}", file=sys.stderr)
        return 1

    print("[live-e2e] registration succeeded.")
    print(f"  client_id: {client_id}")
    print(f"  client_secret: {_mask_secret(client_secret)}")
    print(f"  user_info: {user_info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
