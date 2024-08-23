# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.hire.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: ProtectAgencyRequest = ProtectAgencyRequest.builder() \
		.user_id_type("open_id") \
		.request_body(ProtectAgencyRequestBody.builder()
					  .talent_id("6962051712422398239")
					  .supplier_id("6898173495386147079")
					  .consultant_id("ou_f476cb099ac9227c9bae09ce46112579")
					  .protect_create_time(1610695587000)
					  .protect_expire_time(1626333987000)
					  .comment("此候选人非常优秀，建议录用。")
					  .current_salary("15k * 13")
					  .expected_salary("18k * 16")
					  .build()) \
		.build()

	# 发起请求
	response: ProtectAgencyResponse = client.hire.v1.agency.protect(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.agency.protect failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: ProtectAgencyRequest = ProtectAgencyRequest.builder() \
		.user_id_type("open_id") \
		.request_body(ProtectAgencyRequestBody.builder()
					  .talent_id("6962051712422398239")
					  .supplier_id("6898173495386147079")
					  .consultant_id("ou_f476cb099ac9227c9bae09ce46112579")
					  .protect_create_time(1610695587000)
					  .protect_expire_time(1626333987000)
					  .comment("此候选人非常优秀，建议录用。")
					  .current_salary("15k * 13")
					  .expected_salary("18k * 16")
					  .build()) \
		.build()

	# 发起请求
	response: ProtectAgencyResponse = await client.hire.v1.agency.aprotect(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.agency.aprotect failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
