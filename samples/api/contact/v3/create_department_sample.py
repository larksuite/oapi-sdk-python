# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.contact.v3 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: CreateDepartmentRequest = CreateDepartmentRequest.builder() \
        .user_id_type("user_id") \
        .department_id_type("open_department_id") \
        .client_token("473469C7-AA6F-4DC5-B3DB-A3DC0DE3C83E") \
        .request_body(Department.builder()
                      .name("DemoName")
                      .i18n_name(DepartmentI18nName.builder().build())
                      .parent_department_id("D067")
                      .department_id("str")
                      .leader_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .order("100")
                      .create_group_chat(False)
                      .leaders([])
                      .group_chat_employee_types([])
                      .department_hrbps([])
                      .build()) \
        .build()

    # 发起请求
    response: CreateDepartmentResponse = client.contact.v3.department.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.contact.v3.department.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: CreateDepartmentRequest = CreateDepartmentRequest.builder() \
        .user_id_type("user_id") \
        .department_id_type("open_department_id") \
        .client_token("473469C7-AA6F-4DC5-B3DB-A3DC0DE3C83E") \
        .request_body(Department.builder()
                      .name("DemoName")
                      .i18n_name(DepartmentI18nName.builder().build())
                      .parent_department_id("D067")
                      .department_id("str")
                      .leader_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .order("100")
                      .create_group_chat(False)
                      .leaders([])
                      .group_chat_employee_types([])
                      .department_hrbps([])
                      .build()) \
        .build()

    # 发起请求
    response: CreateDepartmentResponse = await client.contact.v3.department.acreate(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.contact.v3.department.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()
