# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.corehr.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: LeaveTypesLeaveRequest = LeaveTypesLeaveRequest.builder() \
		.page_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") \
		.page_size("100") \
		.status("1") \
		.user_id_type("people_corehr_id") \
		.build()

	# 发起请求
	response: LeaveTypesLeaveResponse = client.corehr.v1.leave.leave_types(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave.leave_types failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: LeaveTypesLeaveRequest = LeaveTypesLeaveRequest.builder() \
		.page_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") \
		.page_size("100") \
		.status("1") \
		.user_id_type("people_corehr_id") \
		.build()

	# 发起请求
	response: LeaveTypesLeaveResponse = await client.corehr.v1.leave.aleave_types(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave.aleave_types failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
