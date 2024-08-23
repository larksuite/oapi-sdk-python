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
	request: LeaveBalancesLeaveRequest = LeaveBalancesLeaveRequest.builder() \
		.page_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") \
		.page_size("20") \
		.as_of_date("2022-07-29") \
		.employment_id_list([]) \
		.user_id_type("people_corehr_id") \
		.time_zone("Asia/Shanghai") \
		.build()

	# 发起请求
	response: LeaveBalancesLeaveResponse = client.corehr.v1.leave.leave_balances(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave.leave_balances failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: LeaveBalancesLeaveRequest = LeaveBalancesLeaveRequest.builder() \
		.page_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9") \
		.page_size("20") \
		.as_of_date("2022-07-29") \
		.employment_id_list([]) \
		.user_id_type("people_corehr_id") \
		.time_zone("Asia/Shanghai") \
		.build()

	# 发起请求
	response: LeaveBalancesLeaveResponse = await client.corehr.v1.leave.aleave_balances(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave.aleave_balances failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
