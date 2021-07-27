# -*- coding: UTF-8 -*-

from larksuiteoapi.api import Request, FormData, FormDataFile, set_timeout, set_path_params, set_query_params, \
    set_is_response_stream, set_response_stream, set_tenant_key, set_need_help_desk_auth

from larksuiteoapi import Config, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER, ACCESS_TOKEN_TYPE_APP, \
    APP_TICKET_KEY_PREFIX, DOMAIN_FEISHU, LEVEL_ERROR, LEVEL_DEBUG

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings(app_id='cli_a04677****8d01b',
                                                app_secret='XcplX2QLU7X******VJKHd6Yzvt',
                                                verification_token='', encrypt_key='',
                                                help_desk_id='696874*****390932',
                                                help_desk_token='ht-c82db92*******f5cf6e569aa')

# for redis store and logger(level=debug)
# conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)

# for memory store and logger(level=debug)
conf = Config("https://open.feishu-boe.cn", app_settings, log_level=LEVEL_DEBUG)


def test_ticket_detail():
    req = Request('/open-apis/helpdesk/v1/tickets/6971250929135779860', 'GET', ACCESS_TOKEN_TYPE_TENANT, None,
                  request_opts=[set_timeout(3), set_need_help_desk_auth()])
    resp = req.do(conf)
    print('header = %s' % resp.get_header().items())
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    test_ticket_detail()
