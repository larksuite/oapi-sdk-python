# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.report.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: QueryTaskRequest = QueryTaskRequest.builder() \
        .user_id_type("user_id") \
        .request_body(QueryTaskRequestBody.builder()
                      .commit_start_time(1622427266)
                      .commit_end_time(1622427266)
                      .rule_id("6894419345318182932")
                      .user_id("ou_133f0b6d0f097cf7d7ba00b38fffb110")
                      .page_token("6895699275733778451")
                      .page_size(10)
                      .build()) \
        .build()

    # 发起请求
    response: QueryTaskResponse = client.report.v1.task.query(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.report.v1.task.query failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: QueryTaskRequest = QueryTaskRequest.builder() \
        .user_id_type("user_id") \
        .request_body(QueryTaskRequestBody.builder()
                      .commit_start_time(1622427266)
                      .commit_end_time(1622427266)
                      .rule_id("6894419345318182932")
                      .user_id("ou_133f0b6d0f097cf7d7ba00b38fffb110")
                      .page_token("6895699275733778451")
                      .page_size(10)
                      .build()) \
        .build()

    # 发起请求
    response: QueryTaskResponse = await client.report.v1.task.aquery(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.report.v1.task.aquery failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()
