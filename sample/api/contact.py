# -*- coding: UTF-8 -*-
from larksuiteoapi.service.contact.v3 import Service as ContactV3Service, User, model
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

service = ContactV3Service(conf)

if __name__ == '__main__':
    # body
    body = User()
    body.name = 'rename'
    body.mobile = '34567'
    departmentIds1 = ['1', '2']
    body.department_ids = departmentIds1
    customAttrs1 = []
    userCustomAttr1 = model.UserCustomAttr()
    userCustomAttr1.type = '1'
    customAttrs1.append(userCustomAttr1)
    userCustomAttr2 = model.UserCustomAttr()
    userCustomAttr2.type = '2'
    customAttrs1.append(userCustomAttr2)
    body.custom_attrs = customAttrs1
    req = service.users.patch(body=body, user_access_token='u-rrrrr')

    # path
    req.set_user_id('open_id')

    resp = req.do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)

