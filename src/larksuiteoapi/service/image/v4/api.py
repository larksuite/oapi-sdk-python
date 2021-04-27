# -*- coding: UTF-8 -*-
# Code generated by lark suite oapi sdk gen

from typing import *

from ....api import Request, Response, set_timeout, set_tenant_key, set_user_access_token, set_path_params, \
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

    def get(self, tenant_key=None, response_stream=None, timeout=None):
        # type: (str, Union[None, IO], int) -> ImageGetReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if tenant_key is not None:
            request_opts += [set_tenant_key(tenant_key)]

        if response_stream is not None:
            request_opts += [set_response_stream(response_stream)]

        return ImageGetReqCall(self, request_opts=request_opts)

    def put(self, tenant_key=None, timeout=None):
        # type: (str, int) -> ImagePutReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if tenant_key is not None:
            request_opts += [set_tenant_key(tenant_key)]

        return ImagePutReqCall(self, request_opts=request_opts)



class ImageGetReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (ImageService, List[Any]) -> None

        self.service = service
        
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_image_key(self, image_key):
        # type: (str) -> ImageGetReqCall
        self.query_params['image_key'] = image_key
        return self

    def do(self):
        # type: () -> Response[None]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_query_params(self.query_params)]
        self.request_opts += [set_is_response_stream()]
        req = Request('image/v4/get', 'GET', [ACCESS_TOKEN_TYPE_TENANT],
                      None, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class ImagePutReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (ImageService, List[Any]) -> None

        self.service = service
        self.body = FormData()

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_image(self, image):
        # type: (IO[Any]) -> ImagePutReqCall
        self.body.add_file('image', FormDataFile(image))
        return self

    def set_image_type(self, image_type):
        # type: (str) -> ImagePutReqCall
        self.body.add_param('image_type', image_type)
        return self

    def do(self):
        # type: () -> Response[Image]
        root_service = self.service.service

        conf = root_service.conf
        req = Request('image/v4/put', 'POST', [ACCESS_TOKEN_TYPE_TENANT], self.body, output_class=Image , request_opts=self.request_opts)
        resp = req.do(conf)
        return resp

