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
	request: CreateLeaveGrantingRecordRequest = CreateLeaveGrantingRecordRequest.builder() \
		.user_id_type("open_id") \
		.request_body(CreateLeaveGrantingRecordRequestBody.builder()
					  .leave_type_id("7111688079785723436")
					  .employment_id("6982509313466189342")
					  .granting_quantity("0.5")
					  .granting_unit(1)
					  .effective_date("2022-01-01")
					  .expiration_date("2022-01-01")
					  .section_type(1)
					  .reason([])
					  .external_id("111")
					  .build()) \
		.build()

	# 发起请求
	response: CreateLeaveGrantingRecordResponse = client.corehr.v1.leave_granting_record.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave_granting_record.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CreateLeaveGrantingRecordRequest = CreateLeaveGrantingRecordRequest.builder() \
		.user_id_type("open_id") \
		.request_body(CreateLeaveGrantingRecordRequestBody.builder()
					  .leave_type_id("7111688079785723436")
					  .employment_id("6982509313466189342")
					  .granting_quantity("0.5")
					  .granting_unit(1)
					  .effective_date("2022-01-01")
					  .expiration_date("2022-01-01")
					  .section_type(1)
					  .reason([])
					  .external_id("111")
					  .build()) \
		.build()

	# 发起请求
	response: CreateLeaveGrantingRecordResponse = await client.corehr.v1.leave_granting_record.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.leave_granting_record.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
