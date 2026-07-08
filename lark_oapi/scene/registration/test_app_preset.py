import base64
import gzip
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, quote, urlparse

from lark_oapi.scene import registration


def _parse_query(url):
    return parse_qs(urlparse(url).query)


def _decode_addons(encoded):
    padding = "=" * (-len(encoded) % 4)
    raw = base64.urlsafe_b64decode((encoded + padding).encode("ascii"))
    return json.loads(gzip.decompress(raw).decode("utf-8"))


class AppAddonsEncodingTest(unittest.TestCase):
    def test_round_trips_full_addons_object(self):
        addons = {
            "scopes": {
                "tenant": ["im:message:send_as_bot", "drive:drive.metadata:readonly"],
                "user": ["calendar:calendar:read"],
            },
            "events": {
                "items": {
                    "tenant": ["im.message.receive_v1"],
                    "user": ["calendar.calendar.event.changed_v4"],
                }
            },
            "callbacks": {"items": ["card.action.trigger"]},
        }

        encoded = registration._encode_addons(addons)

        self.assertRegex(encoded, r"^[A-Za-z0-9_-]+$")
        self.assertEqual(_decode_addons(encoded), addons)

    def test_rejects_unknown_top_level_keys(self):
        with self.assertRaisesRegex(ValueError, r"addons\.security is not allowed"):
            registration._encode_addons({
                "scopes": {"tenant": ["im:message:send_as_bot"]},
                "security": {"allowed_ips": ["1.2.3.4"]},
            })

    def test_rejects_unknown_nested_keys(self):
        with self.assertRaisesRegex(ValueError, r"addons\.scopes\.bot is not allowed"):
            registration._encode_addons({"scopes": {"bot": ["x"]}})

        with self.assertRaisesRegex(ValueError, r"addons\.events\.items\.app is not allowed"):
            registration._encode_addons({"events": {"items": {"app": ["x"]}}})

    def test_rejects_invalid_leaf_values(self):
        with self.assertRaisesRegex(ValueError, r"addons\.scopes\.tenant must be a list of strings"):
            registration._encode_addons({"scopes": {"tenant": "im:message:send_as_bot"}})

        with self.assertRaisesRegex(ValueError, r"addons\.callbacks\.items\[1\] must be a non-empty string"):
            registration._encode_addons({"callbacks": {"items": ["card.action.trigger", ""]}})

    def test_rejects_empty_addons(self):
        match = r"at least one scope, event or callback"
        with self.assertRaisesRegex(ValueError, match):
            registration._encode_addons({})
        with self.assertRaisesRegex(ValueError, match):
            registration._encode_addons({"scopes": {"tenant": [], "user": []}})


class AppPresetQRCodeURLTest(unittest.TestCase):
    def _build_url(
            self,
            app_preset=None,
            source=None,
            raw_url="https://accounts.feishu.cn/page/launcher?ticket=abc",
            addons=None,
            create_only=None,
            app_id=None,
    ):
        flow = registration._RegistrationFlow(
            on_qr_code=lambda info: None,
            on_status_change=None,
            source=source,
            domain="https://accounts.feishu.cn",
            lark_domain="https://accounts.larksuite.com",
            app_preset=app_preset,
            addons=addons,
            create_only=create_only,
            app_id=app_id,
        )
        return flow._build_qr_url(raw_url)

    def test_omits_app_preset_params_when_not_provided(self):
        url = self._build_url()
        query = _parse_query(url)

        self.assertNotIn("avatar", query)
        self.assertNotIn("name", query)
        self.assertNotIn("desc", query)
        self.assertNotIn("addons", query)
        self.assertNotIn("createOnly", query)
        self.assertNotIn("clientID", query)
        self.assertEqual(query["from"], ["sdk"])
        self.assertEqual(query["tp"], ["sdk"])
        self.assertEqual(query["source"], ["python-sdk"])
        self.assertEqual(query["ticket"], ["abc"])

    def test_keeps_source_with_app_preset(self):
        url = self._build_url(app_preset={"name": "X"}, source="lark-cli")
        query = _parse_query(url)

        self.assertEqual(query["source"], ["python-sdk/lark-cli"])
        self.assertEqual(query["name"], ["X"])

    def test_accepts_single_avatar_string(self):
        url = self._build_url(app_preset={"avatar": "https://example.com/a.png"})
        query = _parse_query(url)

        self.assertEqual(query["avatar"], ["https://example.com/a.png"])

    def test_accepts_avatar_list_and_preserves_order(self):
        avatars = [
            "https://example.com/a.png",
            "https://example.com/b.webp",
            "https://example.com/c.gif",
        ]

        url = self._build_url(app_preset={"avatar": avatars})
        query = _parse_query(url)

        self.assertEqual(query["avatar"], avatars)

    def test_accepts_exactly_six_avatars(self):
        avatars = [f"https://example.com/{index}.png" for index in range(6)]

        url = self._build_url(app_preset={"avatar": avatars})
        query = _parse_query(url)

        self.assertEqual(query["avatar"], avatars)

    def test_rejects_more_than_six_avatars(self):
        avatars = [f"https://example.com/{index}.png" for index in range(7)]

        with self.assertRaisesRegex(ValueError, r"at most 6 URLs, got 7"):
            self._build_url(app_preset={"avatar": avatars})

    def test_rejects_empty_avatar_list(self):
        with self.assertRaisesRegex(ValueError, r"at least 1 URL"):
            self._build_url(app_preset={"avatar": []})

    def test_rejects_empty_avatar_string(self):
        with self.assertRaisesRegex(ValueError, r"avatar\[0\].*non-empty string"):
            self._build_url(app_preset={"avatar": ""})

    def test_rejects_empty_avatar_list_item_with_index(self):
        with self.assertRaisesRegex(ValueError, r"avatar\[1\].*non-empty string"):
            self._build_url(app_preset={"avatar": ["https://example.com/a.png", ""]})

    def test_url_encodes_name_with_user_placeholder(self):
        name = "{user}的应用"

        url = self._build_url(app_preset={"name": name})
        query = _parse_query(url)

        self.assertEqual(query["name"], [name])
        self.assertIn(f"name={quote(name)}", url)

    def test_url_encodes_desc(self):
        desc = "由业务平台自动生成"

        url = self._build_url(app_preset={"desc": desc})
        query = _parse_query(url)

        self.assertEqual(query["desc"], [desc])
        self.assertIn(f"desc={quote(desc)}", url)

    def test_emits_all_app_preset_fields(self):
        url = self._build_url(
            app_preset={
                "avatar": ["https://example.com/a.png", "https://example.com/b.png"],
                "name": "MyApp",
                "desc": "demo",
            }
        )
        query = _parse_query(url)

        self.assertEqual(query["avatar"], ["https://example.com/a.png", "https://example.com/b.png"])
        self.assertEqual(query["name"], ["MyApp"])
        self.assertEqual(query["desc"], ["demo"])

    def test_encodes_addons_param(self):
        addons = {
            "scopes": {"tenant": ["im:message:send_as_bot"], "user": ["calendar:calendar:read"]},
            "events": {"items": {"tenant": ["im.message.receive_v1"]}},
            "callbacks": {"items": ["card.action.trigger"]},
        }

        url = self._build_url(addons=addons)
        query = _parse_query(url)

        self.assertEqual(_decode_addons(query["addons"][0]), addons)

    def test_keeps_addons_with_app_preset_and_create_only(self):
        url = self._build_url(
            app_preset={"name": "MyApp"},
            addons={"scopes": {"tenant": ["im:message:send_as_bot"]}},
            create_only=True,
        )
        query = _parse_query(url)

        self.assertEqual(_decode_addons(query["addons"][0]), {"scopes": {"tenant": ["im:message:send_as_bot"]}})
        self.assertEqual(query["name"], ["MyApp"])
        self.assertEqual(query["createOnly"], ["true"])

    def test_sets_client_id_from_app_id(self):
        url = self._build_url(app_id="cli_a1b2c3")
        query = _parse_query(url)

        self.assertEqual(query["clientID"], ["cli_a1b2c3"])

    def test_omits_create_only_when_false(self):
        url = self._build_url(create_only=False)
        query = _parse_query(url)

        self.assertNotIn("createOnly", query)

    def test_rejects_empty_app_id(self):
        with self.assertRaisesRegex(ValueError, r"app_id must be a non-empty string"):
            self._build_url(app_id="")


class AddonsPresetEncodingTest(unittest.TestCase):
    def test_accepts_preset_false_alone_as_minimal_base_payload(self):
        encoded = registration._encode_addons({"preset": False})

        self.assertEqual(_decode_addons(encoded), {"preset": False})

    def test_keeps_preset_false_alongside_scope_entries(self):
        addons = {"preset": False, "scopes": {"tenant": ["im:message:send_as_bot"]}}

        encoded = registration._encode_addons(addons)

        self.assertEqual(_decode_addons(encoded), addons)

    def test_preserves_explicit_preset_true_in_payload(self):
        addons = {"preset": True, "scopes": {"tenant": ["x"]}}

        encoded = registration._encode_addons(addons)

        self.assertEqual(_decode_addons(encoded), addons)

    def test_rejects_non_boolean_preset_values(self):
        # 1 和 0 在 Python 里是 bool 的父类 int 的值，容易被 isinstance(x, int)
        # 式的校验误放行，必须与字符串、None 一样显式拒绝。
        for value in ("false", 1, 0, None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, r"addons\.preset must be a boolean"):
                    registration._encode_addons({"preset": value})

    def test_preset_false_does_not_relax_top_level_key_whitelist(self):
        with self.assertRaisesRegex(ValueError, r"addons\.security is not allowed"):
            registration._encode_addons({
                "preset": False,
                "security": {"allowed_ips": ["1.2.3.4"]},
            })

    def test_rejects_preset_true_without_any_entries(self):
        with self.assertRaisesRegex(ValueError, r"at least one scope, event or callback"):
            registration._encode_addons({"preset": True})

    def test_keeps_rejecting_empty_addons_without_preset(self):
        # 回归护栏：引入 preset 后，缺省的空 payload 仍必须沿用既有报错，
        # 逐字不变——preset 相关的提示语只允许出现在显式传了 preset 时。
        match = r"^addons must contain at least one scope, event or callback$"
        with self.assertRaisesRegex(ValueError, match):
            registration._encode_addons({})
        with self.assertRaisesRegex(ValueError, match):
            registration._encode_addons({"scopes": {"tenant": []}})

    def test_accepts_preset_false_with_empty_scope_lists(self):
        addons = {"preset": False, "scopes": {"tenant": []}}

        encoded = registration._encode_addons(addons)

        self.assertEqual(_decode_addons(encoded), addons)

    def test_omits_preset_key_when_not_provided(self):
        encoded = registration._encode_addons({"scopes": {"tenant": ["x"]}})

        self.assertNotIn("preset", _decode_addons(encoded))


class AddonsPresetQRCodeURLTest(unittest.TestCase):
    def test_addons_query_param_carries_preset_false(self):
        addons = {"preset": False, "scopes": {"tenant": ["im:message:send_as_bot"]}}
        flow = registration._RegistrationFlow(
            on_qr_code=lambda info: None,
            on_status_change=None,
            source=None,
            domain="https://accounts.feishu.cn",
            lark_domain="https://accounts.larksuite.com",
            app_preset=None,
            addons=addons,
            create_only=None,
            app_id=None,
        )

        url = flow._build_qr_url("https://accounts.feishu.cn/page/launcher?ticket=abc")
        query = _parse_query(url)

        self.assertEqual(_decode_addons(query["addons"][0]), addons)
        self.assertEqual(query["from"], ["sdk"])
        self.assertEqual(query["tp"], ["sdk"])
        self.assertEqual(query["source"], ["python-sdk"])
        self.assertEqual(query["ticket"], ["abc"])


def _device_flow_responses():
    return [
        {"supported_auth_methods": ["client_secret"]},
        {
            "device_code": "dev-1",
            "verification_uri_complete": "https://accounts.feishu.cn/page/launcher",
            "interval": 1,
            "expires_in": 60,
        },
        {
            "client_id": "cli_a",
            "client_secret": "sec_a",
            "user_info": {"open_id": "ou_x", "tenant_brand": "feishu"},
        },
    ]


class AddonsPresetRegisterAppE2ETest(unittest.TestCase):
    def test_sync_register_app_passes_addons_preset_to_qr_url(self):
        responses = _device_flow_responses()

        def fake_post(self, data):
            return responses.pop(0)

        addons = {"preset": False, "scopes": {"tenant": ["im:message:send_as_bot"]}}
        captured = {}
        with patch.object(registration._SyncFlow, "_post", fake_post):
            result = registration.register_app(
                on_qr_code=lambda info: captured.update(info),
                addons=addons,
            )

        query = _parse_query(captured["url"])
        self.assertEqual(_decode_addons(query["addons"][0]), addons)
        self.assertEqual(result["client_id"], "cli_a")
        self.assertEqual(result["client_secret"], "sec_a")


class AddonsPresetAsyncRegisterAppE2ETest(unittest.IsolatedAsyncioTestCase):
    async def test_async_register_app_passes_addons_preset_to_qr_url(self):
        responses = _device_flow_responses()

        async def fake_post(self, data):
            return responses.pop(0)

        # 近空应用场景：最小底座 + 无任何增量条目，走完整异步注册链路。
        addons = {"preset": False}
        captured = {}
        with patch.object(registration._AsyncFlow, "_post", fake_post):
            result = await registration.aregister_app(
                on_qr_code=lambda info: captured.update(info),
                addons=addons,
            )

        query = _parse_query(captured["url"])
        self.assertEqual(_decode_addons(query["addons"][0]), addons)
        self.assertEqual(result["client_id"], "cli_a")
        self.assertEqual(result["client_secret"], "sec_a")


class AppPresetRegisterAppE2ETest(unittest.TestCase):
    def test_sync_register_app_passes_app_preset_to_qr_url(self):
        responses = [
            {"supported_auth_methods": ["client_secret"]},
            {
                "device_code": "dev-1",
                "verification_uri_complete": "https://accounts.feishu.cn/page/launcher",
                "interval": 1,
                "expires_in": 60,
            },
            {
                "client_id": "cli_a",
                "client_secret": "sec_a",
                "user_info": {"open_id": "ou_x", "tenant_brand": "feishu"},
            },
        ]

        def fake_post(self, data):
            return responses.pop(0)

        captured = {}
        with patch.object(registration._SyncFlow, "_post", fake_post):
            result = registration.register_app(
                on_qr_code=lambda info: captured.update(info),
                app_preset={
                    "avatar": ["https://example.com/a.png", "https://example.com/b.webp"],
                    "name": "{user}的应用",
                    "desc": "由业务平台自动生成",
                },
                addons={"scopes": {"tenant": ["im:message:send_as_bot"]}},
                create_only=True,
                app_id="cli_a1b2c3",
            )

        query = _parse_query(captured["url"])
        self.assertEqual(query["avatar"], ["https://example.com/a.png", "https://example.com/b.webp"])
        self.assertEqual(query["name"], ["{user}的应用"])
        self.assertEqual(query["desc"], ["由业务平台自动生成"])
        self.assertEqual(_decode_addons(query["addons"][0]), {"scopes": {"tenant": ["im:message:send_as_bot"]}})
        self.assertEqual(query["createOnly"], ["true"])
        self.assertEqual(query["clientID"], ["cli_a1b2c3"])
        self.assertEqual(result["client_id"], "cli_a")
        self.assertEqual(result["client_secret"], "sec_a")


class AppPresetAsyncRegisterAppE2ETest(unittest.IsolatedAsyncioTestCase):
    async def test_async_register_app_passes_app_preset_to_qr_url(self):
        responses = [
            {"supported_auth_methods": ["client_secret"]},
            {
                "device_code": "dev-1",
                "verification_uri_complete": "https://accounts.feishu.cn/page/launcher",
                "interval": 1,
                "expires_in": 60,
            },
            {
                "client_id": "cli_a",
                "client_secret": "sec_a",
                "user_info": {"open_id": "ou_x", "tenant_brand": "feishu"},
            },
        ]

        async def fake_post(self, data):
            return responses.pop(0)

        captured = {}
        with patch.object(registration._AsyncFlow, "_post", fake_post):
            result = await registration.aregister_app(
                on_qr_code=lambda info: captured.update(info),
                app_preset={
                    "avatar": "https://example.com/a.png",
                    "name": "{user}的应用",
                    "desc": "由业务平台自动生成",
                },
                addons={"callbacks": {"items": ["card.action.trigger"]}},
                create_only=True,
                app_id="cli_a1b2c3",
            )

        query = _parse_query(captured["url"])
        self.assertEqual(query["avatar"], ["https://example.com/a.png"])
        self.assertEqual(query["name"], ["{user}的应用"])
        self.assertEqual(query["desc"], ["由业务平台自动生成"])
        self.assertEqual(_decode_addons(query["addons"][0]), {"callbacks": {"items": ["card.action.trigger"]}})
        self.assertEqual(query["createOnly"], ["true"])
        self.assertEqual(query["clientID"], ["cli_a1b2c3"])
        self.assertEqual(result["client_id"], "cli_a")
        self.assertEqual(result["client_secret"], "sec_a")
