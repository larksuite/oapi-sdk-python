# -*- coding: UTF-8 -*-


from typing import Union

from .consts import HTTP_HEADER_KEY_REQUEST_ID, HTTP_KEY_STATUS_CODE


class Context(object):
    def __init__(self):
        # type: () -> None
        self.__data = {}

    def get(self, key):  # type: (str) -> Union[None, str]
        return self.__data.get(key)

    def set(self, key, value):  # type: (str, str) -> bool
        self.__data[key] = value
        return True

    def set_request_id(self, log_id, request_id):
        # type: (Union[None, str], Union[None, str]) -> None
        if log_id:
            self.__data[HTTP_HEADER_KEY_REQUEST_ID] = log_id
        else:
            self.__data[HTTP_HEADER_KEY_REQUEST_ID] = request_id

    def set_http_status_code(self, code):  # type: (int) -> None
        self.__data[HTTP_KEY_STATUS_CODE] = code

    def get_request_id(self):  # type: () -> Union[None, str]
        return self.__data.get(HTTP_HEADER_KEY_REQUEST_ID)

    def get_http_status_code(self):  # type: () -> Union[None, int]
        return self.__data.get(HTTP_KEY_STATUS_CODE)
