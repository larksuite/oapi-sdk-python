# -*- coding: UTF-8 -*-
from larksuiteoapi.service.contact.v3 import Service as ContactService, model
from larksuiteoapi import DOMAIN_FEISHU, Config, LEVEL_DEBUG, LEVEL_INFO, \
    LEVEL_WARN, LEVEL_ERROR

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key），非必需，订阅事件、消息卡片时必需
# 更多介绍请看：Github -> README.zh.md -> 如何构建应用配置（AppSettings）
app_settings = Config.new_internal_app_settings(app_id='AppID', app_secret='AppSecret',
                                                verification_token='VerificationToken', encrypt_key='EncryptKey')

# 当前访问的是飞书，使用默认内存存储、默认日志（Error 级别）
# 更多介绍请看：Github -> README.zh.md -> 如何构建整体配置（Config）
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_ERROR)

service = ContactService(conf)

if __name__ == '__main__':
    # body params
    body = model.User()
    body.name = ''
    body.mobile = ''
    department_ids_1 = []
    body.department_ids = department_ids_1
    body.employee_type = 0
    req_call = service.users.create(body=body)

    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('HTTP status code = %s' % resp.get_http_status_code())
    print('HTTP response header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)