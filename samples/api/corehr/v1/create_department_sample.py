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
	request: CreateDepartmentRequest = CreateDepartmentRequest.builder() \
		.client_token("12454646") \
		.user_id_type("people_corehr_id") \
		.department_id_type("people_corehr_department_id") \
		.request_body(DepartmentCreate.builder()
					  .sub_type(Enum.builder().build())
					  .manager("6893013238632416776")
					  .is_confidential(True)
					  .hiberarchy_common(HiberarchyCommon.builder().build())
					  .effective_time("2020-05-01 00:00:00")
					  .custom_fields([])
					  .cost_center_id("7142384817131652652")
					  .staffing_model(Enum.builder().build())
					  .build()) \
		.build()

	# 发起请求
	response: CreateDepartmentResponse = client.corehr.v1.department.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.department.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
		.client_token("12454646") \
		.user_id_type("people_corehr_id") \
		.department_id_type("people_corehr_department_id") \
		.request_body(DepartmentCreate.builder()
					  .sub_type(Enum.builder().build())
					  .manager("6893013238632416776")
					  .is_confidential(True)
					  .hiberarchy_common(HiberarchyCommon.builder().build())
					  .effective_time("2020-05-01 00:00:00")
					  .custom_fields([])
					  .cost_center_id("7142384817131652652")
					  .staffing_model(Enum.builder().build())
					  .build()) \
		.build()

	# 发起请求
	response: CreateDepartmentResponse = await client.corehr.v1.department.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.department.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
