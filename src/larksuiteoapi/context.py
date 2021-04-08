# -*- coding: UTF-8 -*-


from typing import Union, Any

from .consts import HTTP_HEADER_KEY_REQUEST_ID, HTTP_KEY_STATUS_CODE, HTTP_HEADER_KEY, HTTP_HEADER_KEY_LOG_ID
from .model import OapiHeader


class Context(object):
    def __init__(self):
        # type: () -> None
        self.__data = {}

    def get(self, key):  # type: (str) -> Union[None, Any]
        return self.__data.get(key)

    def set(self, key, value):  # type: (str, Any) -> bool
        self.__data[key] = value
        return True

    def set_request_id(self, log_id, request_id):
        # type: (Union[None, str], Union[None, str]) -> None
        if log_id:
            self.__data[HTTP_HEADER_KEY_REQUEST_ID] = log_id
        else:
            self.__data[HTTP_HEADER_KEY_REQUEST_ID] = request_id

    def get_header(self):  # type: () -> OapiHeader
        header = self.__data[HTTP_HEADER_KEY]
        if header:
            return header
        return OapiHeader()

    def get_request_id(self):  # type: () -> Union[None, str]
        header = self.get_header()
        log_id = header.first_value(HTTP_HEADER_KEY_LOG_ID)
        if log_id:
            return log_id
        return header.first_value(HTTP_HEADER_KEY_REQUEST_ID)

    def get_http_status_code(self):  # type: () -> Union[None, int]
        return self.__data.get(HTTP_KEY_STATUS_CODE)
