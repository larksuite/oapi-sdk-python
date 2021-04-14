# -*- coding: UTF-8 -*-
from larksuiteoapi.service.im.v1 import Service as ImV1Service, MessageCreateReqBody
from larksuiteoapi import DOMAIN_FEISHU, Store, Config, AppSettings, Logger, LEVEL_DEBUG, LEVEL_INFO, \
    LEVEL_WARN, LEVEL_ERROR, DefaultLogger

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key）。
# 更多介绍请看：Github->README.zh.md->高级使用->如何构建应用配置（AppSettings）
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别）
# 更多介绍请看：Github->README.zh.md->高级使用->如何构建整体配置（Config）
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)

service = ImV1Service(conf)

if __name__ == '__main__':
    # body
    body = MessageCreateReqBody()
    body.content = '{"text":"<at user_id=\\"ou_a11d2bcc7d852afbcaf37e5b3ad01f7e\\">Tom</at> test content"}'
    body.msg_type = 'text'
    body.receive_id = 'ou_a11d2bcc7d852afbcaf37e5b3ad01f7e'
    req_call = service.messages.create(body=body)
    req_call.set_receive_id_type('open_id')
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)

