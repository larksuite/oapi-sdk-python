# -*- coding: UTF-8 -*-

class AppSettings(object):
    """
    This class is to storage basic app_type, app_id, app_secret for application.
    """

    def __init__(self, app_type, app_id, app_secret, verification_token, encrypt_key):
        # type: (str, str, str, str, str) -> None
        self.app_type = app_type
        self.app_id = app_id
        self.app_secret = app_secret
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
