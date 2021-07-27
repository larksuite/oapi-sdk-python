# -*- coding: UTF-8 -*-

class APIError(Exception):
    def __init__(self, message=''):  # type: (str) -> None
        super(APIError, self).__init__(message)
        self.message = message


# Errors

ERR_ACCESS_TOKEN_TYPE_INVALID = APIError(message='access token type is invalid')
ERR_TENANT_KEY_IS_EMPTY = APIError(message='tenant key is empty')
ERR_USER_ACCESS_TOKEN_KEY_IS_EMPTY = APIError(message='user access token is empty')
ERR_APP_TICKET_IS_EMPTY = APIError(message='app ticket is empty')
ERR_HELP_DESK_AUTH_EMPTY = APIError(message='help desk API, please set the helpdesk information of AppSettings')
