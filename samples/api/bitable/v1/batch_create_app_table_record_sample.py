# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
        .app_token("appbcbWCzen6D8dezhoCH2RpMAh") \
        .table_id("tblsRc9GRRXKqhvW") \
        .user_id_type("user_id") \
        .client_token("fe599b60-450f-46ff-b2ef-9f6675625b97") \
        .request_body(BatchCreateAppTableRecordRequestBody.builder()
                      .records([])
                      .build()) \
        .build()

    # 发起请求
    response: BatchCreateAppTableRecordResponse = client.bitable.v1.app_table_record.batch_create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.batch_create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
        .app_token("appbcbWCzen6D8dezhoCH2RpMAh") \
        .table_id("tblsRc9GRRXKqhvW") \
        .user_id_type("user_id") \
        .client_token("fe599b60-450f-46ff-b2ef-9f6675625b97") \
        .request_body(BatchCreateAppTableRecordRequestBody.builder()
                      .records([])
                      .build()) \
        .build()

    # 发起请求
    response: BatchCreateAppTableRecordResponse = await client.bitable.v1.app_table_record.abatch_create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.abatch_create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()