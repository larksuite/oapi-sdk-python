import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, quote, urlparse

from lark_oapi.scene import registration


def _parse_query(url):
    return parse_qs(urlparse(url).query)


class AppPresetQRCodeURLTest(unittest.TestCase):
    def _build_url(self, app_preset=None, source=None, raw_url="https://accounts.feishu.cn/page/launcher?ticket=abc"):
        flow = registration._RegistrationFlow(
            on_qr_code=lambda info: None,
            on_status_change=None,
            source=source,
            domain="https://accounts.feishu.cn",
            lark_domain="https://accounts.larksuite.com",
            app_preset=app_preset,
        )
        return flow._build_qr_url(raw_url)

    def test_omits_app_preset_params_when_not_provided(self):
        url = self._build_url()
        query = _parse_query(url)

        self.assertNotIn("avatar", query)
        self.assertNotIn("name", query)
        self.assertNotIn("desc", query)
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
            )

        query = _parse_query(captured["url"])
        self.assertEqual(query["avatar"], ["https://example.com/a.png", "https://example.com/b.webp"])
        self.assertEqual(query["name"], ["{user}的应用"])
        self.assertEqual(query["desc"], ["由业务平台自动生成"])
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
            )

        query = _parse_query(captured["url"])
        self.assertEqual(query["avatar"], ["https://example.com/a.png"])
        self.assertEqual(query["name"], ["{user}的应用"])
        self.assertEqual(query["desc"], ["由业务平台自动生成"])
        self.assertEqual(result["client_id"], "cli_a")
        self.assertEqual(result["client_secret"], "sec_a")
