# -*- coding: UTF-8 -*-

from typing import IO, Any, Callable, Dict, List, Tuple, Union, TypeVar, Generic

import requests

from ...model import OapiHeader
from ... import VERSION
from ...config import Config
from ...consts import *
from ...context import Context
from ...api.api_error import APIError, ERR_ACCESS_TOKEN_TYPE_INVALID, ERR_TENANT_KEY_IS_EMPTY, \
    ERR_USER_ACCESS_TOKEN_KEY_IS_EMPTY, ERR_APP_TICKET_IS_EMPTY, ERR_HELP_DESK_AUTH_EMPTY
from ..response.response import Response, ResponseError
from ..tokens import *
from .form_data import FormData
from ...consts import ERR_CODE_OK
from ...utils.dt import make_datatype, to_json

T = TypeVar('T')


class Option(object):
    def __init__(self):
        # type: () -> None
        self.no_data_field = False  # type: bool
        self.user_access_token = ''  # type: str
        self.tenant_key = ''  # type: str
        self.is_response_stream = False  # type: bool
        self.path_params = {}  # type: Union[None, Dict[str, str]]
        self.query_params = {}  # type: Union[None, Dict[str, str]]
        self.timeout = 30  # type: Union[None, int]
        self.response_stream_file = None  # type: Union[None, IO[Any]]
        self.need_help_desk_auth = False  # type: bool


class Request(Generic[T]):

    def __init__(self, http_path, http_method, access_token_types, request_body, output_class=dict, request_opts=None):
        # type: (str, str, Union[List[str], str], Any, T, List[Callable[[Option], Any]]) -> None

        if request_opts:
            # type: List[Callable[[Option], Any]]
            self.request_opts = request_opts
        else:
            self.request_opts = []  # type: List[Callable[[Option], Any]]

        self.http_path = http_path
        self.http_method = http_method
        if isinstance(access_token_types, str):
            access_token_types = [access_token_types]

        self.accessible_token_type_list = sorted(access_token_types)

        if self.accessible_token_type_list.count(ACCESS_TOKEN_TYPE_TENANT) > 0:
            self.access_token_type = ACCESS_TOKEN_TYPE_TENANT
        else:
            self.access_token_type = self.accessible_token_type_list[0]

        self.request_body = request_body
        self.output_class = output_class
        self.query_params = {}  # type: Dict[str, str]
        self.response_body = b''  # type: bytes
        self.tenant_key = ''  # type: str
        self.user_access_token = ''  # type: str
        self.content_type = ''  # type: str

        self.is_retry = False  # type: bool
        self.is_response_stream = False  # type: bool
        self.is_response_stream_current = False  # type: bool
        self.response_stream_file = None  # type: Union[None, IO[Any]]
        self.need_help_desk_auth = False  # type: bool
        self.no_data_field = False  # type: bool
        self.timeout = None  # type: Union[None, int]

        self.session = requests.Session()  # type: requests.Session
        self.response = None  # type: Union[requests.Response, None]

    def prepare(self):  # type: () -> None
        option = Option()
        for operation_fn in self.request_opts:
            operation_fn(option)
        self.no_data_field = option.no_data_field
        self.is_response_stream = option.is_response_stream
        self.response_stream_file = option.response_stream_file
        self.need_help_desk_auth = option.need_help_desk_auth

        if option.tenant_key != "" \
                and self.accessible_token_type_list.count(ACCESS_TOKEN_TYPE_TENANT):
            self.access_token_type = ACCESS_TOKEN_TYPE_TENANT
            self.tenant_key = option.tenant_key

        if option.user_access_token != "" \
                and self.accessible_token_type_list.count(ACCESS_TOKEN_TYPE_USER):
            self.access_token_type = ACCESS_TOKEN_TYPE_USER
            self.user_access_token = option.user_access_token

        if option.query_params is not None:
            self.query_params = option.query_params

        if option.path_params is not None:
            self.http_path = resolve_path(self.http_path, option.path_params)

        if option.timeout is not None:
            self.timeout = option.timeout

    @staticmethod
    def send_by_auth(path, method, body):
        # type: (str, str, Union[bytes, str, FormData]) -> Request
        req = Request(path, method, [ACCESS_TOKEN_TYPE_NONE], body)
        req.request_opts += [set_no_data_field()]
        return req

    def set_authorization_to_header(self, token):  # type: (str) -> None
        self.session.headers['Authorization'] = ('Bearer %s' % token)

    def set_helpdesk_authorization_to_header(self, token):  # type: (str) -> None
        self.session.headers['X-Lark-Helpdesk-Authorization'] = token

    def do_request(self, config):  # type: (Config) -> requests.Response
        method, path = self.http_method, self.http_path
        params, body = self.query_params, self.request_body
        session = self.session

        if isinstance(body, FormData):
            config.logger.debug("request http_path:%s, http_method:%s, access_token_type:%s, request body:%s" % (
                self.http_path, self.http_method, self.access_token_type, body))

            files, data, need_close = body.to_map()
            try:
                self.is_response_stream = True
                self.response = session.request(
                    method, path, files=files, data=data, stream=True, timeout=self.timeout)
            finally:
                for file in need_close:
                    file.close()
        else:
            config.logger.debug("request http_path:%s, http_method:%s, access_token_type:%s, request body:%s" % (
                self.http_path, self.http_method, self.access_token_type, self.request_body))
            if self.content_type:
                session.headers[CONTENT_TYPE] = self.content_type

            if self.response_stream_file:
                self.response = session.request(method, path, params=params, data=body, stream=True,
                                                timeout=self.timeout)
            else:
                self.response = session.request(method, path, params=params, data=body, timeout=self.timeout)

        return self.response

    def prepare_body(self):  # type: () -> None
        if isinstance(self.request_body, FormData):
            for file in self.request_body.files:
                file.prepare()
            return

        body = self.request_body
        if body:
            self.content_type = DEFAULT_CONTENT_TYPE

        if body is None:
            self.request_body = None
        elif isinstance(body, str):
            self.request_body = body.encode('utf-8')
        elif isinstance(body, bytes):
            self.request_body = body
        elif isinstance(body, dict):
            self.request_body = json.dumps(body)
        elif isinstance(body, object):
            self.request_body = json.dumps(to_json(body))
        else:
            raise APIError(message='Unrecognized request_body type')

    def do(self, conf):
        # type: (Config) -> Response[T]
        return Handlers(conf, self).handle()


DEFAULT_MAX_RETRY_COUNT = 1
DEFAULT_HTTP_REQUEST_HEADERS = {
    "User-Agent": "oapi-sdk-python/%s" % VERSION
}


class Handlers(object):
    def __init__(self, config, req, resp=None):
        # type: (Config, Request, Response) -> None
        self.ctx = Context()
        self.config = config
        self.req = req
        self.resp = resp

    def prepare(self):  # type: () -> None
        self.req.prepare()
        req, conf = self.req, self.config

        if not req.http_path.startswith("http"):
            if req.http_path.startswith("/open-apis/"):
                req.http_path = "%s%s" % (conf.domain, req.http_path)
            else:
                req.http_path = "%s/%s/%s" % (conf.domain, OAPI_ROOT_PATH, req.http_path)

    def validate(self):  # type: () -> None
        req, config = self.req, self.config
        if req.access_token_type == ACCESS_TOKEN_TYPE_NONE:
            return

        if not req.accessible_token_type_list.count(req.access_token_type):
            raise ERR_ACCESS_TOKEN_TYPE_INVALID

        if req.access_token_type == ACCESS_TOKEN_TYPE_USER and req.user_access_token == '':
            raise ERR_USER_ACCESS_TOKEN_KEY_IS_EMPTY

        settings = config.app_settings
        if settings.app_type == APP_TYPE_ISV:
            if req.access_token_type == ACCESS_TOKEN_TYPE_TENANT and req.tenant_key == '':
                raise ERR_TENANT_KEY_IS_EMPTY

    def build(self):  # type: () -> None
        req = self.req
        if not req.is_retry:
            req.prepare_body()

        for (k, v) in DEFAULT_HTTP_REQUEST_HEADERS.items():
            req.session.headers[k] = v
        if req.content_type is not None and req.content_type != "":
            req.session.headers[CONTENT_TYPE] = req.content_type

    def sign(self):  # type: () -> None
        req = self.req
        if req.access_token_type == ACCESS_TOKEN_TYPE_APP:
            AccessToken(self).set_app_access_token()
        elif req.access_token_type == ACCESS_TOKEN_TYPE_TENANT:
            AccessToken(self).set_tenant_access_token()
        elif req.access_token_type == ACCESS_TOKEN_TYPE_USER:
            AccessToken(self).set_user_access_token()

        if req.need_help_desk_auth:
            if self.config.helpDeskAuthorization:
                req.set_helpdesk_authorization_to_header(self.config.helpDeskAuthorization)
            else:
                raise ERR_HELP_DESK_AUTH_EMPTY

    def send(self):  # type: () -> None
        req = self.req
        self.build()
        self.sign()
        req.do_request(self.config)
        ctx, resp = self.ctx, req.response
        ctx.set(HTTP_HEADER_KEY, OapiHeader(resp.headers))
        ctx.set(HTTP_KEY_STATUS_CODE, resp.status_code)

        self.validate_response()
        self.parse_response()
        self.retry()

    def validate_response(self):  # type: () -> None
        conf, req = self.config, self.req
        resp = req.response
        content_type = resp.headers.get(CONTENT_TYPE)
        if req.is_response_stream:
            if content_type.count(CONTENT_TYPE_JSON):
                req.is_response_stream_current = False
                return
            if resp.status_code != 200:
                raise APIError(message="response status_code:%d, not equal 200, body:%s" % (
                    resp.status_code, resp.content))

            req.is_response_stream_current = True
            return

        if not content_type or not content_type.count(CONTENT_TYPE_JSON):
            raise APIError(
                message='response request_id:%s, status_code: %d, content-type: %s, body: %s ' % (
                            self.ctx.get_request_id(), resp.status_code, content_type, resp.content)
            )

    def parse_response(self):  # type: () -> None
        resp = Response(self.ctx)
        self.resp = resp
        if self.req.is_response_stream_current:
            if self.req.response_stream_file:
                for buffer in self.req.response.iter_content(chunk_size=2048):
                    self.req.response_stream_file.write(buffer)
                resp.data = self.req.response_stream_file
            else:
                resp.data = self.req.response.content
            self.req.response.close()
            return

        resp_json = self.req.response.json()
        self.config.logger.debug("request http_path:%s, response status code:%d, response body:%s" % (
            self.req.http_path, self.req.response.status_code, resp_json))
        if isinstance(resp_json, dict):
            resp.code = resp_json.get('code')
            resp.msg = resp_json.get('msg')
            resp.error = make_datatype(ResponseError, resp_json.get('error'))
            if self.req.no_data_field:
                resp.data = make_datatype(self.req.output_class, resp_json)
            else:
                resp.data = make_datatype(self.req.output_class, resp_json.get('data'))

    def retry(self):  # type: () -> None
        self.req.is_retry = RETRY_CODE.count(self.resp.code) > 0

    def complement(self, exception):  # type: (Exception) -> None
        if isinstance(self.req.request_body, FormData):
            self.req.request_body.delete_tmp_files()

        if exception == ERR_APP_TICKET_IS_EMPTY:
            AccessToken(self).apply_app_ticket()

        if exception:
            return

        if self.resp.code == ERR_CODE_APP_TICKET_INVALID:
            AccessToken(self).apply_app_ticket()

    def handle(self):  # type: () -> Response
        conf, req = self.config, self.req
        exception = None  # type:Exception
        try:
            self.prepare()
            self.validate()
            for _ in range(DEFAULT_MAX_RETRY_COUNT + 1):
                self.send()
                if not req.is_retry:
                    return self.resp
        except Exception as e:
            exception = e
            raise e
        finally:
            self.complement(exception)
        return self.resp


class AccessToken(object):
    def __init__(self, handlers):  # type: (Handlers) -> None
        self.handlers = handlers

    def apply_app_ticket(self):  # type: () -> None
        config = self.handlers.config
        req_body = ApplyAppTicketReq(
            config.app_settings.app_id, config.app_settings.app_secret)
        req = Request.send_by_auth(APPLY_APP_TICKET_PATH, "POST", req_body.__str__())
        resp = Handlers(config, req).handle()
        if resp.code == ERR_CODE_OK:
            config.logger.info("Already applied app ticket")
        else:
            config.logger.error(resp.__str__())

    def set_app_access_token_to_store(self, access_token):
        # type: (AppAccessToken) -> None

        token, expire = access_token.app_access_token, access_token.expire
        conf = self.handlers.config
        key = '%s-%s' % (APP_ACCESS_TOKEN_KEY_PREFIX, conf.app_settings.app_id)
        try:
            conf.store.set(key, token, expire - EXPIRE_DELTA)
        except Exception as e:
            conf.logger.warn('storage app_access_token into storage occurred an error:%s' % e.__str__())

    def set_tenant_access_token_to_store(self, access_token):
        # type: (TenantAccessToken) -> None

        req = self.handlers.req
        token, expire = access_token.tenant_access_token, access_token.expire
        tenant_key = req.tenant_key
        conf = self.handlers.config
        key = '%s-%s-%s' % (TENANT_ACCESS_TOKEN_KEY_PREFIX,
                            conf.app_settings.app_id, tenant_key)
        try:
            conf.store.set(key, token, expire - EXPIRE_DELTA)
        except Exception as e:
            conf.logger.warn(
                'storage tenant_access_token into storage occurred an error:%s' % e.__str__())

    def get_internal_app_access_token(self):  # type: () -> AppAccessToken
        conf = self.handlers.config
        internal_access_token_request = InternalAccessTokenReq(
            conf.app_settings.app_id, conf.app_settings.app_secret)
        req_json = internal_access_token_request.__str__()
        req = Request.send_by_auth(
            APP_ACCESS_TOKEN_INTERNAL_URL_PATH, 'POST', req_json)
        resp = Handlers(conf, req).handle()
        if resp.code != ERR_CODE_OK:
            raise APIError("obtain internal app access token，failure information:%s" % resp)
        return AppAccessToken(resp.data['app_access_token'], resp.data['expire'])

    def get_isv_app_access_token(self):
        # type: () -> AppAccessToken
        find, app_ticket = self.get_app_ticket()
        if not find:
            raise ERR_APP_TICKET_IS_EMPTY

        conf = self.handlers.config
        settings = conf.app_settings

        isv_app_access_token_req = ISVAppAccessTokenReq(
            settings.app_id, settings.app_secret, app_ticket)
        req_json = isv_app_access_token_req.__str__()

        req = Request.send_by_auth(
            APP_ACCESS_TOKEN_ISV_URL_PATH, 'POST', req_json)
        resp = Handlers(conf, req).handle()
        if resp.code != ERR_CODE_OK:
            raise APIError("obtain isv app access token，failure information:%s" % resp)
        return AppAccessToken(resp.data['app_access_token'], resp.data['expire'])

    def get_isv_tenant_access_token(self):
        # type: () -> Tuple[AppAccessToken, TenantAccessToken]
        app_access_token = self.get_isv_app_access_token()
        tenant_key = self.handlers.req.tenant_key

        isv_tenant_access_token_req = ISVTenantAccessTokenReq(
            app_access_token.app_access_token, tenant_key)
        req_json = isv_tenant_access_token_req.__str__()

        req = Request.send_by_auth(
            TENANT_ACCESS_TOKEN_ISV_URL_PATH, 'POST', req_json)
        resp = Handlers(self.handlers.config, req).handle()
        if resp.code != ERR_CODE_OK:
            raise APIError("obtain isv tenant access token，failure information:%s" % resp)
        tenant_access_token = TenantAccessToken(resp.data['tenant_access_token'], resp.data['expire'])
        return app_access_token, tenant_access_token

    def set_app_access_token(self):  # type: () -> None
        conf, req = self.handlers.config, self.handlers.req
        if not req.is_retry:
            key = '%s-%s' % (APP_ACCESS_TOKEN_KEY_PREFIX, conf.app_settings.app_id)
            find, token = conf.store.get(key)
            if find and token != "":
                req.set_authorization_to_header(token)
                return

        if conf.app_settings.app_type == APP_TYPE_INTERNAL:
            app_access_token = self.get_internal_app_access_token()
        else:  # isv app access token
            app_access_token = self.get_isv_app_access_token()

        self.set_app_access_token_to_store(app_access_token)
        req.set_authorization_to_header(app_access_token.app_access_token)

    def set_user_access_token(self):  # type: () -> None
        req = self.handlers.req
        if req.user_access_token != "":
            req.set_authorization_to_header(req.user_access_token)

    def set_tenant_access_token(self):  # type: () -> None
        conf, req = self.handlers.config, self.handlers.req
        tenant_key = req.tenant_key
        if not req.is_retry:
            key = '%s-%s-%s' % (TENANT_ACCESS_TOKEN_KEY_PREFIX,
                                conf.app_settings.app_id, tenant_key)
            find, token = conf.store.get(key)
            if find and token != "":
                req.set_authorization_to_header(token)
                return

        if conf.app_settings.app_type == APP_TYPE_INTERNAL:
            tenant_access_token = self.get_internal_tenant_access_token()
        else:  # isv app access token
            app_access_token, tenant_access_token = self.get_isv_tenant_access_token()
            if app_access_token is not None:
                self.set_app_access_token_to_store(app_access_token)

        self.set_tenant_access_token_to_store(tenant_access_token)
        req.set_authorization_to_header(
            tenant_access_token.tenant_access_token)

    def get_app_ticket(self):  # type: () -> Tuple[bool, str]
        config = self.handlers.config
        store = config.store

        key = '%s-%s' % (APP_TICKET_KEY_PREFIX, config.app_settings.app_id)
        return store.get(key)

    def get_internal_tenant_access_token(self):
        # type: () -> TenantAccessToken
        conf = self.handlers.config
        settings = conf.app_settings

        internal_access_token_req = InternalAccessTokenReq(
            settings.app_id, settings.app_secret)
        req_json = internal_access_token_req.__str__()

        req = Request.send_by_auth(
            TENANT_ACCESS_TOKEN_INTERNAL_URL_PATH, 'POST', req_json)
        resp = Handlers(self.handlers.config, req).handle()
        if resp.code != ERR_CODE_OK:
            raise APIError("obtain internal tenant access token，failure information:%s" % resp)
        return TenantAccessToken(resp.data['tenant_access_token'], resp.data['expire'])


def set_timeout(timeout):
    # type: (Union[int, float]) -> Callable[[Option], Any]
    """
    timeout unit: seconds
    """

    def fn(option):  # type: (Option) -> None
        option.timeout = timeout

    return fn


def set_user_access_token(user_access_token):
    # type: (str) -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.user_access_token = user_access_token

    return fn


def set_tenant_key(tenant_key):
    # type: (str) -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.tenant_key = tenant_key

    return fn


def set_query_params(query_params):
    # type: (Dict[str, str]) -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.query_params = query_params

    return fn


def set_path_params(path_params):
    # type: (Dict[str, str]) -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.path_params = path_params

    return fn


def set_no_data_field():
    # type: () -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.no_data_field = True

    return fn


def set_is_response_stream():
    # type: () -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.is_response_stream = True

    return fn


def set_response_stream(stream):
    # type: (IO[Any]) -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.is_response_stream = True
        option.response_stream_file = stream

    return fn


def set_need_help_desk_auth():
    # type: () -> Callable[[Option], Any]

    def fn(option):  # type: (Option) -> None
        option.need_help_desk_auth = True

    return fn


def resolve_path(path, path_variables):  # type: (str, Dict[str, str]) -> str
    splatted = path.split('/')
    for i in range(len(splatted)):
        if splatted[i].startswith(':'):
            k = splatted[i][1:]
            v = path_variables.get(splatted[i][1:], '')
            if v == '':
                raise RuntimeError("http path:%s, param name `%s` not found value" % (path, k))
            splatted[i] = v
    return '/'.join(splatted)
