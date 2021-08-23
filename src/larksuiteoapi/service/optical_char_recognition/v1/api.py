# -*- coding: UTF-8 -*-
# Code generated by lark suite oapi sdk gen

from typing import *

from ....api import Request as APIRequest, Response as APIResponse, set_timeout, set_tenant_key, set_user_access_token, set_path_params, \
    set_query_params, set_response_stream, set_is_response_stream, FormData, FormDataFile
from ....config import Config
from ....consts import ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER, ACCESS_TOKEN_TYPE_APP
from .model import *


class Service(object):
    def __init__(self, conf):
        # type: (Config) -> None
        self.conf = conf
        self.images = ImageService(self)
        



class ImageService(object):
    def __init__(self, service):
        # type: (Service) -> None
        self.service = service

    def basic_recognize(self, body, tenant_key=None, timeout=None):
        # type: (ImageBasicRecognizeReqBody, str, int) -> ImageBasicRecognizeReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if tenant_key is not None:
            request_opts += [set_tenant_key(tenant_key)]

        return ImageBasicRecognizeReqCall(self, body, request_opts=request_opts)



class ImageBasicRecognizeReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (ImageService, ImageBasicRecognizeReqBody, List[Any]) -> None

        self.service = service
        self.body = body

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def do(self):
        # type: () -> APIResponse[Type[ImageBasicRecognizeResult]]
        root_service = self.service.service

        conf = root_service.conf
        req = APIRequest('/open-apis/optical_char_recognition/v1/image/basic_recognize', 'POST', [ACCESS_TOKEN_TYPE_TENANT],
                        self.body, output_class=ImageBasicRecognizeResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp

