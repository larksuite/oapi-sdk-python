import subprocess
import sys
from pathlib import Path


def test_root_import_defers_generated_api_and_optional_modules():
    repo_root = Path(__file__).resolve().parents[3]
    script = """
import sys
import lark_oapi

assert not any(name.startswith('lark_oapi.api.') for name in sys.modules)
assert 'lark_oapi.ws' not in sys.modules
assert 'lark_oapi.event.dispatcher_handler' not in sys.modules

client = lark_oapi.Client.builder().app_id('app').app_secret('secret').build()
assert 'lark_oapi.api.wiki.service' not in sys.modules
assert client.wiki is client.wiki
assert 'lark_oapi.api.wiki.service' in sys.modules
assert 'lark_oapi.api.im.service' not in sys.modules
assert client.im is client.im
assert 'lark_oapi.api.im.service' in sys.modules

assert lark_oapi.im is lark_oapi.api.im
assert 'lark_oapi.api.payroll' not in sys.modules
assert {'ws', 'EventDispatcherHandler'} <= set(dir(lark_oapi))
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
