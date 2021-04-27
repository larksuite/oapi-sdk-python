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
        self.apps = AppService(self)
        self.app_tables = AppTableService(self)
        self.app_table_fields = AppTableFieldService(self)
        self.app_table_records = AppTableRecordService(self)
        



class AppService(object):
    def __init__(self, service):
        # type: (Service) -> None
        self.service = service

    def get(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppGetReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppGetReqCall(self, request_opts=request_opts)


class AppTableService(object):
    def __init__(self, service):
        # type: (Service) -> None
        self.service = service

    def list(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppTableListReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableListReqCall(self, request_opts=request_opts)


class AppTableFieldService(object):
    def __init__(self, service):
        # type: (Service) -> None
        self.service = service

    def list(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppTableFieldListReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableFieldListReqCall(self, request_opts=request_opts)


class AppTableRecordService(object):
    def __init__(self, service):
        # type: (Service) -> None
        self.service = service

    def batch_delete(self, body, user_access_token=None, timeout=None):
        # type: (AppTableRecordBatchDeleteReqBody, str, int) -> AppTableRecordBatchDeleteReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordBatchDeleteReqCall(self, body, request_opts=request_opts)

    def batch_create(self, body, user_access_token=None, timeout=None):
        # type: (AppTableRecordBatchCreateReqBody, str, int) -> AppTableRecordBatchCreateReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordBatchCreateReqCall(self, body, request_opts=request_opts)

    def get(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppTableRecordGetReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordGetReqCall(self, request_opts=request_opts)

    def update(self, body, user_access_token=None, timeout=None):
        # type: (AppTableRecord, str, int) -> AppTableRecordUpdateReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordUpdateReqCall(self, body, request_opts=request_opts)

    def delete(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppTableRecordDeleteReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordDeleteReqCall(self, request_opts=request_opts)

    def list(self, user_access_token=None, timeout=None):
        # type: (str, int) -> AppTableRecordListReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordListReqCall(self, request_opts=request_opts)

    def batch_update(self, body, user_access_token=None, timeout=None):
        # type: (AppTableRecordBatchUpdateReqBody, str, int) -> AppTableRecordBatchUpdateReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordBatchUpdateReqCall(self, body, request_opts=request_opts)

    def create(self, body, user_access_token=None, timeout=None):
        # type: (AppTableRecord, str, int) -> AppTableRecordCreateReqCall

        request_opts = []   # type: List[Callable[[Any], Any]]

        if timeout is not None:
            request_opts += [set_timeout(timeout)]

        if user_access_token is not None:
            request_opts += [set_user_access_token(user_access_token)]

        return AppTableRecordCreateReqCall(self, body, request_opts=request_opts)



class AppTableRecordBatchDeleteReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (AppTableRecordService, AppTableRecordBatchDeleteReqBody, List[Any]) -> None

        self.service = service
        self.body = body
        self.path_params = {}   # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordBatchDeleteReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordBatchDeleteReqCall
        self.path_params['table_id'] = table_id
        return self

    def do(self):
        # type: () -> Response[AppTableRecordBatchDeleteResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/batch_delete', 'POST', [ACCESS_TOKEN_TYPE_USER],
                      self.body, output_class=AppTableRecordBatchDeleteResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordBatchCreateReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (AppTableRecordService, AppTableRecordBatchCreateReqBody, List[Any]) -> None

        self.service = service
        self.body = body
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordBatchCreateReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordBatchCreateReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_user_id_type(self, user_id_type):
        # type: (str) -> AppTableRecordBatchCreateReqCall
        self.query_params['user_id_type'] = user_id_type
        return self

    def do(self):
        # type: () -> Response[AppTableRecordBatchCreateResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/batch_create', 'POST', [ACCESS_TOKEN_TYPE_USER],
                      self.body, output_class=AppTableRecordBatchCreateResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordGetReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppTableRecordService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordGetReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordGetReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_record_id(self, record_id):
        # type: (str) -> AppTableRecordGetReqCall
        self.path_params['record_id'] = record_id
        return self

    def do(self):
        # type: () -> Response[AppTableRecordGetResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/:record_id', 'GET', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=AppTableRecordGetResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordUpdateReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (AppTableRecordService, AppTableRecord, List[Any]) -> None

        self.service = service
        self.body = body
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordUpdateReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordUpdateReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_record_id(self, record_id):
        # type: (str) -> AppTableRecordUpdateReqCall
        self.path_params['record_id'] = record_id
        return self

    def set_user_id_type(self, user_id_type):
        # type: (str) -> AppTableRecordUpdateReqCall
        self.query_params['user_id_type'] = user_id_type
        return self

    def do(self):
        # type: () -> Response[AppTableRecordUpdateResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/:record_id', 'PUT', [ACCESS_TOKEN_TYPE_USER],
                      self.body, output_class=AppTableRecordUpdateResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordDeleteReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppTableRecordService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordDeleteReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordDeleteReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_record_id(self, record_id):
        # type: (str) -> AppTableRecordDeleteReqCall
        self.path_params['record_id'] = record_id
        return self

    def do(self):
        # type: () -> Response[DeleteRecord]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/:record_id', 'DELETE', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=DeleteRecord, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordListReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppTableRecordService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordListReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordListReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_view_id(self, view_id):
        # type: (str) -> AppTableRecordListReqCall
        self.query_params['view_id'] = view_id
        return self

    def set_page_token(self, page_token):
        # type: (str) -> AppTableRecordListReqCall
        self.query_params['page_token'] = page_token
        return self

    def set_page_size(self, page_size):
        # type: (int) -> AppTableRecordListReqCall
        self.query_params['page_size'] = page_size
        return self

    def do(self):
        # type: () -> Response[AppTableRecordListResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records', 'GET', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=AppTableRecordListResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordBatchUpdateReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (AppTableRecordService, AppTableRecordBatchUpdateReqBody, List[Any]) -> None

        self.service = service
        self.body = body
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordBatchUpdateReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordBatchUpdateReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_user_id_type(self, user_id_type):
        # type: (str) -> AppTableRecordBatchUpdateReqCall
        self.query_params['user_id_type'] = user_id_type
        return self

    def do(self):
        # type: () -> Response[AppTableRecordBatchUpdateResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records/batch_update', 'POST', [ACCESS_TOKEN_TYPE_USER],
                      self.body, output_class=AppTableRecordBatchUpdateResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableRecordCreateReqCall(object):
    def __init__(self, service, body, request_opts=None):
        # type: (AppTableRecordService, AppTableRecord, List[Any]) -> None

        self.service = service
        self.body = body
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableRecordCreateReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableRecordCreateReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_user_id_type(self, user_id_type):
        # type: (str) -> AppTableRecordCreateReqCall
        self.query_params['user_id_type'] = user_id_type
        return self

    def do(self):
        # type: () -> Response[AppTableRecordCreateResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/records', 'POST', [ACCESS_TOKEN_TYPE_USER],
                      self.body, output_class=AppTableRecordCreateResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppGetReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppGetReqCall
        self.path_params['app_token'] = app_token
        return self

    def do(self):
        # type: () -> Response[AppGetResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        req = Request('bitable/v1/apps/:app_token', 'GET', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=AppGetResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableListReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppTableService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableListReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_page_token(self, page_token):
        # type: (str) -> AppTableListReqCall
        self.query_params['page_token'] = page_token
        return self

    def set_page_size(self, page_size):
        # type: (int) -> AppTableListReqCall
        self.query_params['page_size'] = page_size
        return self

    def do(self):
        # type: () -> Response[AppTableListResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables', 'GET', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=AppTableListResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp


class AppTableFieldListReqCall(object):
    def __init__(self, service, request_opts=None):
        # type: (AppTableFieldService, List[Any]) -> None

        self.service = service
        
        self.path_params = {}   # type: Dict[str, Any]
        self.query_params = {}  # type: Dict[str, Any]

        if request_opts:
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Any]

    def set_app_token(self, app_token):
        # type: (str) -> AppTableFieldListReqCall
        self.path_params['app_token'] = app_token
        return self

    def set_table_id(self, table_id):
        # type: (str) -> AppTableFieldListReqCall
        self.path_params['table_id'] = table_id
        return self

    def set_view_id(self, view_id):
        # type: (str) -> AppTableFieldListReqCall
        self.query_params['view_id'] = view_id
        return self

    def set_page_token(self, page_token):
        # type: (str) -> AppTableFieldListReqCall
        self.query_params['page_token'] = page_token
        return self

    def set_page_size(self, page_size):
        # type: (int) -> AppTableFieldListReqCall
        self.query_params['page_size'] = page_size
        return self

    def do(self):
        # type: () -> Response[AppTableFieldListResult]
        root_service = self.service.service

        conf = root_service.conf
        self.request_opts += [set_path_params(self.path_params)]
        self.request_opts += [set_query_params(self.query_params)]
        req = Request('bitable/v1/apps/:app_token/tables/:table_id/fields', 'GET', [ACCESS_TOKEN_TYPE_USER],
                      None, output_class=AppTableFieldListResult, request_opts=self.request_opts)
        resp = req.do(conf)
        return resp

