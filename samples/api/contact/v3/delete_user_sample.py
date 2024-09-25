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
    request: DeleteUserRequest = DeleteUserRequest.builder() \
        .user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62") \
        .user_id_type("open_id") \
        .request_body(DeleteUserRequestBody.builder()
                      .department_chat_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .external_chat_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .docs_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .calendar_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .application_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .minutes_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .survey_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .email_acceptor(ResourceAcceptor.builder().build())
                      .anycross_acceptor_user_id("str")
                      .build()) \
        .build()

    # 发起请求
    response: DeleteUserResponse = client.contact.v3.user.delete(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.contact.v3.user.delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: DeleteUserRequest = DeleteUserRequest.builder() \
        .user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62") \
        .user_id_type("open_id") \
        .request_body(DeleteUserRequestBody.builder()
                      .department_chat_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .external_chat_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .docs_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .calendar_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .application_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .minutes_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .survey_acceptor_user_id("ou_7dab8a3d3cdcc9da365777c7ad535d62")
                      .email_acceptor(ResourceAcceptor.builder().build())
                      .anycross_acceptor_user_id("str")
                      .build()) \
        .build()

    # 发起请求
    response: DeleteUserResponse = await client.contact.v3.user.adelete(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.contact.v3.user.adelete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()
