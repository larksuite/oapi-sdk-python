# -*- coding: UTF-8 -*-

import json


class JSONSerializable(object):
    def __str__(self):  # type: () -> str
        d = {}

        for key in self.__dict__.keys():
            if key.startswith('__') or key.endswith('__'):
                continue

            d[key] = self.__getattribute__(key)
        return json.dumps(d)


class ISVTenantAccessTokenReq(JSONSerializable):
    def __init__(self, app_access_token='', tenant_key=''):  # type: (str, str) -> None
        self.app_access_token = app_access_token
        self.tenant_key = tenant_key


class TenantAccessToken(JSONSerializable):
    def __init__(self, tenant_access_token='', expire=''):  # type: (str, int) -> None
        self.expire = expire
        self.tenant_access_token = tenant_access_token


class InternalAccessTokenReq(JSONSerializable):
    def __init__(self, app_id='', app_secret=''):  # type: (str, str) -> None
        self.app_id = app_id
        self.app_secret = app_secret


class ISVAppAccessTokenReq(JSONSerializable):
    def __init__(self, app_id='', app_secret='', app_ticket=''):  # type: (str, str, str) -> None
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_ticket = app_ticket


class AppAccessToken(JSONSerializable):
    def __init__(self, app_access_token='', expire=''):  # type: (str, int) -> None
        self.expire = expire
        self.app_access_token = app_access_token


class ApplyAppTicketReq(JSONSerializable):
    def __init__(self, app_id='', app_secret=''):  # type: (str, str) -> None
        self.app_id = app_id
        self.app_secret = app_secret
