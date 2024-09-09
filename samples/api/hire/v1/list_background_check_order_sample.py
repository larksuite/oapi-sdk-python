# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.hire.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ListBackgroundCheckOrderRequest = ListBackgroundCheckOrderRequest.builder() \
        .user_id_type("open_id") \
        .page_token("eyJvZmZzZXQiOjEsInRpbWVzdGFtcCI6MTY0MDc2NTYzMjA4OCwiaWQiOm51bGx9") \
        .page_size(10) \
        .application_id("6985833807195212076") \
        .update_start_time("1638848468868") \
        .update_end_time("1638848468869") \
        .build()

    # 发起请求
    response: ListBackgroundCheckOrderResponse = client.hire.v1.background_check_order.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.hire.v1.background_check_order.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


# 异步方式
async def amain():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ListBackgroundCheckOrderRequest = ListBackgroundCheckOrderRequest.builder() \
        .user_id_type("open_id") \
        .page_token("eyJvZmZzZXQiOjEsInRpbWVzdGFtcCI6MTY0MDc2NTYzMjA4OCwiaWQiOm51bGx9") \
        .page_size(10) \
        .application_id("6985833807195212076") \
        .update_start_time("1638848468868") \
        .update_end_time("1638848468869") \
        .build()

    # 发起请求
    response: ListBackgroundCheckOrderResponse = await client.hire.v1.background_check_order.alist(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.hire.v1.background_check_order.alist failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()
