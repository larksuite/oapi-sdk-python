# -*- coding: UTF-8 -*-
from larksuiteoapi import Config
from larksuiteoapi.service.image.v4 import Service as ImageV4Service

from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from src.larksuiteoapi import DOMAIN_FEISHU, DOMAIN_LARK_SUITE

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)

# for memory store and logger(level=debug)
# conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)

service = ImageV4Service(conf)


def test_image_put():
    img = open('./test.png', 'rb')
    resp = service.images.put().set_image(img).set_image_type("message").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data.image_key)
    else:
        print(resp.msg)
        print(resp.error)
    img.close()


def test_image_put_bytes():
    img = open('./test.png', 'rb')
    resp = service.images.put().set_image(img.read()).set_image_type("message").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data.image_key)
    else:
        print(resp.msg)
        print(resp.error)
    img.close()


def test_image_get():
    f = open('./aa.png', 'wb')
    resp = service.images.get(response_stream=f).set_image_key("img_a3183080-928f-4bb7-b256-177523c762eg").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code != 0:
        print(resp.msg)
        print(resp.error)
    f.close()


def test_image_get_bytes():
    resp = service.images.get().set_image_key("img_5b1a1887-5039-4176-b6c3-badc77ce5eag").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        f = open('./aa3.png', 'wb')
        f.write(resp.data)
        f.close()
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    # test_image_put()
    # test_image_get()
    # test_image_put_bytes()
    test_image_get_bytes()
