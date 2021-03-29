# -*- coding: UTF-8 -*-


from typing import Dict, ItemsView, List, Union


class OapiHeader(object):
    def __init__(self, data=None):
        # type: (Union[None, Dict[str, List[str]]]) -> None

        self.data = {}  # type: Dict[str, List[str]]
        if data is None:
            self.__append_multiple({})
        else:
            self.__append_multiple(data)

    def __append_multiple(self, headers):
        # type: (Dict[str, Union[str, List[str]]]) -> None
        for k, v in headers.items():
            key = k.lower()

            if self.data.get(key) is None:
                self.data[key] = []

            if not isinstance(v, list):
                v = [v]

            self.data[key] += v

    def append(self, key, value):  # type: (str, Union[str, List[str]]) -> None
        header = {key: value}
        self.__append_multiple(header)

    def get_keys(self):  # type: () -> List[str]
        keys = []
        for key in self.data.keys():
            keys += [key]
        return keys

    def first_value(self, key):  # type: (str) -> Union[None, str]
        val = self.data.get(key.lower())
        if val is None:
            return None

        if isinstance(val, list):
            if len(val) <= 0:
                return None
            else:
                return val[0]

        if isinstance(val, str):
            return val

        return None

    def values(self, key):  # type: (str) -> Union[None, List[str]]
        return self.data.get(key)

    def items(self):  # type: () -> ItemsView[str, List[str]]
        return self.data.items()
