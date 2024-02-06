# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.task.v2 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: PatchTasklistRequest = PatchTasklistRequest.builder() \
        .tasklist_guid("d300a75f-c56a-4be9-80d1-e47653028ceb") \
        .user_id_type("open_id") \
        .request_body(PatchTasklistRequestBody.builder()
                      .tasklist(InputTasklist.builder().build())
                      .update_fields([])
                      .origin_owner_to_role("none")
                      .build()) \
        .build()

    # 发起请求
    response: PatchTasklistResponse = client.task.v2.tasklist.patch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.task.v2.tasklist.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: PatchTasklistRequest = PatchTasklistRequest.builder() \
        .tasklist_guid("d300a75f-c56a-4be9-80d1-e47653028ceb") \
        .user_id_type("open_id") \
        .request_body(PatchTasklistRequestBody.builder()
                      .tasklist(InputTasklist.builder().build())
                      .update_fields([])
                      .origin_owner_to_role("none")
                      .build()) \
        .build()

    # 发起请求
    response: PatchTasklistResponse = await client.task.v2.tasklist.apatch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.task.v2.tasklist.apatch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()