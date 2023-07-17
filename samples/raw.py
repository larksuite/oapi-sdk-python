import lark_oapi as lark


def batch_get_id_user():
    # 创建client
    client = lark.Client.builder() \
        .app_id("APP_ID") \
        .app_secret("APP_SECRET") \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: lark.BaseRequest = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.POST) \
        .uri("/open-apis/contact/v3/users/batch_get_id") \
        .token_types({lark.AccessTokenType.TENANT}) \
        .queries({"user_id_type": "open_id"}) \
        .body({"emails": ["xxxx@bytedance.com"], "mobiles": ["15000000000"]}) \
        .build()

    # 发起请求
    response: lark.BaseResponse = client.request(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.request failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(str(response.raw.content, lark.UTF_8))
