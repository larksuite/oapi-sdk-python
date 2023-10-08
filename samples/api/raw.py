import io

from requests_toolbelt import MultipartEncoder

import lark_oapi as lark


# 通过手机号或邮箱获取用户 ID
def batch_get_id_user():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: lark.BaseRequest = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.POST) \
        .uri("/open-apis/contact/v3/users/batch_get_id") \
        .token_types({lark.AccessTokenType.TENANT}) \
        .queries([("user_id_type", "open_id")]) \
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


# 上传文件
def upload_all_file():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    file = open("/Users/bytedance/Desktop/demo.pdf", "rb")
    data = {
        "file_name": "demo.pdf",
        "parent_type": "explorer",
        "parent_node": "Y9LhfoWNZlKxWcdsf2fcPP0SnXc",
        "size": 1199,
        "file": file
    }
    body = MultipartEncoder(lark.Files.parse_form_data(data))

    request: lark.BaseRequest = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.POST) \
        .uri("/open-apis/drive/v1/files/upload_all") \
        .headers({"Content-Type": body.content_type}) \
        .token_types({lark.AccessTokenType.TENANT}) \
        .body(body) \
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


# 下载文件
def download_file():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: lark.BaseRequest = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.GET) \
        .uri("/open-apis/drive/v1/files/:file_token/download") \
        .paths({"file_token": "TYr6bxn1PoFZb0x63UocDQ5tnBf"}) \
        .token_types({lark.AccessTokenType.TENANT}) \
        .build()

    # 发起请求
    response: lark.BaseResponse = client.request(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.request failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    file = io.BytesIO(response.raw.content)
    file_name = lark.Files.parse_file_name(response.raw.headers)
    f = open(f"/Users/bytedance/Desktop/{file_name}", "wb")
    f.write(file.read())
    f.close()


if __name__ == "__main__":
    pass
