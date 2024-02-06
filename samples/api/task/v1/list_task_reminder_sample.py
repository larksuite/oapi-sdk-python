# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.task.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ListTaskReminderRequest = ListTaskReminderRequest.builder() \
        .task_id("0d38e26e-190a-49e9-93a2-35067763ed1f") \
        .page_size(50) \
        .page_token("「填写上次返回的page_token」") \
        .build()

    # 发起请求
    response: ListTaskReminderResponse = client.task.v1.task_reminder.list(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.task.v1.task_reminder.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: ListTaskReminderRequest = ListTaskReminderRequest.builder() \
        .task_id("0d38e26e-190a-49e9-93a2-35067763ed1f") \
        .page_size(50) \
        .page_token("「填写上次返回的page_token」") \
        .build()

    # 发起请求
    response: ListTaskReminderResponse = await client.task.v1.task_reminder.alist(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.task.v1.task_reminder.alist failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()