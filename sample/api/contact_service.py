# -*- coding: UTF-8 -*-
from larksuiteoapi.service.contact.v3 import Service as ContactV3Service, User

from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from larksuiteoapi import DOMAIN_FEISHU, DOMAIN_LARK_SUITE, Config

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)

# for memory store and logger(level=debug)
# conf = test_config_with_memory_store(DOMAIN_FEISHU, app_settings)

service = ContactV3Service(conf)


def test_user_patch():
    user = User()
    user.name = "rename"
    resp = service.users.patch(user).set_user_id("77bbc392").set_user_id_type("user_id").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data.user)
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    test_user_patch()
