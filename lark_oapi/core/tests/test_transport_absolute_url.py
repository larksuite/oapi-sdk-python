from lark_oapi.core.http.transport import _build_url


def test_build_url_keeps_absolute_http_url():
    url = _build_url(
        "https://open.feishu.cn",
        "http://127.0.0.1:18080/oauth/v3/token",
        {},
    )

    assert url == "http://127.0.0.1:18080/oauth/v3/token"


def test_build_url_keeps_absolute_https_url():
    url = _build_url(
        "https://open.feishu.cn",
        "https://accounts.feishu.cn/oauth/v3/token",
        {},
    )

    assert url == "https://accounts.feishu.cn/oauth/v3/token"


def test_build_url_relative_path_unchanged():
    url = _build_url(
        "https://open.feishu.cn",
        "/open-apis/mock/v1/ping",
        {},
    )

    assert url == "https://open.feishu.cn/open-apis/mock/v1/ping"
