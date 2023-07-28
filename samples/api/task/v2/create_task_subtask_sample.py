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
    request: CreateTaskSubtaskRequest = CreateTaskSubtaskRequest.builder() \
        .task_guid("e297ddff-06ca-4166-b917-4ce57cd3a7a0") \
        .user_id_type("open_id") \
        .request_body(InputTask.builder()
                      .summary("针对全年销售进行一次复盘")
                      .description("需要事先阅读复盘总结文档")
                      .due(Due.builder().build())
                      .origin(Origin.builder().build())
                      .extra("dGVzdA==")
                      .completed_at("0")
                      .members([])
                      .repeat_rule("FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR")
                      .custom_complete(CustomComplete.builder().build())
                      .tasklists([])
                      .client_token("daa2237f-8310-4707-a83b-52c8a81e0fb7")
                      .start(Start.builder().build())
                      .reminders([])
                      .build()) \
        .build()

    # 发起请求
    response: CreateTaskSubtaskResponse = client.task.v2.task_subtask.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.task.v2.task_subtask.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()
