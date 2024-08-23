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
	request: AddEnumOptionCommonDataMetaDataRequest = AddEnumOptionCommonDataMetaDataRequest.builder() \
		.client_token("6727817538283013641") \
		.request_body(AddEnumOptionCommonDataMetaDataRequestBody.builder()
					  .object_api_name("probation_management")
					  .enum_field_api_name("final_assessment_grade")
					  .enum_field_options([])
					  .build()) \
		.build()

	# 发起请求
	response: AddEnumOptionCommonDataMetaDataResponse = client.corehr.v1.common_data_meta_data.add_enum_option(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.common_data_meta_data.add_enum_option failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: AddEnumOptionCommonDataMetaDataRequest = AddEnumOptionCommonDataMetaDataRequest.builder() \
		.client_token("6727817538283013641") \
		.request_body(AddEnumOptionCommonDataMetaDataRequestBody.builder()
					  .object_api_name("probation_management")
					  .enum_field_api_name("final_assessment_grade")
					  .enum_field_options([])
					  .build()) \
		.build()

	# 发起请求
	response: AddEnumOptionCommonDataMetaDataResponse = await client.corehr.v1.common_data_meta_data.aadd_enum_option(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.common_data_meta_data.aadd_enum_option failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
