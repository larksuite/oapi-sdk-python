# -*- coding: UTF-8 -*-

from larksuiteoapi.service.calendar.v4.api import Service as CalendarV4Service
from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from larksuiteoapi import DOMAIN_FEISHU, DOMAIN_LARK_SUITE, Config

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)

# for memory store and logger(level=debug)
# conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)


def test_calendar_acls_delete():
    service = CalendarV4Service(conf)
    resp = service.calendar_acls.delete().set_calendar_id("calendar_id").set_acl_id("aclId").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data.user)
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    test_calendar_acls_delete()
