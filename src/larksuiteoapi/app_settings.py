# -*- coding: UTF-8 -*-

import base64

import sys

PY3 = sys.version_info[0] == 3


class AppSettings(object):
    """
    This class is to storage basic app_type, app_id, app_secret for application.
    """

    def __init__(self, app_type, app_id, app_secret, verification_token='', encrypt_key='', help_desk_id='',
                 help_desk_token=''):
        # type: (str, str, str, str, str, str, str) -> None
        self.app_type = app_type
        self.app_id = app_id
        self.app_secret = app_secret
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
        self.help_desk_id = help_desk_id
        self.help_desk_token = help_desk_token

    def get_help_desk_authorization(self):
        # type: () -> str
        if self.help_desk_id == '' or self.help_desk_token == '':
            return ''
        token = self.help_desk_id + ':' + self.help_desk_token
        if PY3:
            return base64.b64encode(token.encode('utf-8')).decode('utf-8')
        else:
            return base64.b64encode(token)
