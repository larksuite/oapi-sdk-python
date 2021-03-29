# -*- coding: UTF-8 -*-


from typing import Dict, List, Union

from .oapi_header import OapiHeader


class OapiResponse(object):
    def __init__(self, status_code=200, content_type='', body=b'', header=None):
        # type: (int, str, bytes, Union[OapiHeader, Dict[str, Union[None, str, List[str]]]]) -> None
        self.status_code = status_code
        self.content_type = content_type
        self.body = body

        if header is None:
            header = {}

        if isinstance(header, dict):
            self.header = OapiHeader(data=header)
        else:
            self.header = header
