# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.attendance.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: PatchLeaveAccrualRecordRequest = PatchLeaveAccrualRecordRequest.builder() \
        .leave_id("1") \
        .user_id_type("open_id") \
        .request_body(PatchLeaveAccrualRecordRequestBody.builder()
                      .leave_granting_record_id("1")
                      .employment_id("1")
                      .leave_type_id("1")
                      .reason([])
                      .time_offset(480)
                      .expiration_date("2020-01-01")
                      .quantity("1")
                      .build()) \
        .build()

    # 发起请求
    response: PatchLeaveAccrualRecordResponse = client.attendance.v1.leave_accrual_record.patch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.attendance.v1.leave_accrual_record.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: PatchLeaveAccrualRecordRequest = PatchLeaveAccrualRecordRequest.builder() \
        .leave_id("1") \
        .user_id_type("open_id") \
        .request_body(PatchLeaveAccrualRecordRequestBody.builder()
                      .leave_granting_record_id("1")
                      .employment_id("1")
                      .leave_type_id("1")
                      .reason([])
                      .time_offset(480)
                      .expiration_date("2020-01-01")
                      .quantity("1")
                      .build()) \
        .build()

    # 发起请求
    response: PatchLeaveAccrualRecordResponse = await client.attendance.v1.leave_accrual_record.apatch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.attendance.v1.leave_accrual_record.apatch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()