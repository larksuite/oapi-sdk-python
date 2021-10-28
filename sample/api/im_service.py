# -*- coding: UTF-8 -*-
from larksuiteoapi.service.im.v1 import Service as ImService, model
from larksuiteoapi import DOMAIN_FEISHU, Store, Config, AppSettings, Logger, LEVEL_DEBUG, LEVEL_INFO, \
    LEVEL_WARN, LEVEL_ERROR, DefaultLogger

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key）。
# 更多介绍请看：Github->README.zh.md->如何构建应用配置（AppSettings）
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Error级别）
# 更多介绍请看：Github->README.zh.md->如何构建整体配置（Config）
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)

service = ImService(conf)


def test_message_create():
    # body
    body = model.MessageCreateReqBody()
    body.content = '{"text":"<at user_id=\\"ou_a11d2bcc7d852afbcaf37e5b3ad01f7e\\">Tom</at> test content"}'
    body.msg_type = 'text'
    body.receive_id = 'ou_a11d2bcc7d852afbcaf37e5b3ad01f7e'
    req_call = service.messages.create(body)
    req_call.set_receive_id_type('open_id')
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data.message_id)
    else:
        print(resp.msg)
        print(resp.error)


def test_image_upload():
    img = open('test.png', 'rb')
    req_call = service.images.create().set_image(img.read()).set_image_type("message")
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    if resp.code == 0:
        print(resp.data.image_key)
    else:
        print(resp.msg)
    print(resp.error)


if __name__ == '__main__':
    #test_message_create()
    test_image_upload()
