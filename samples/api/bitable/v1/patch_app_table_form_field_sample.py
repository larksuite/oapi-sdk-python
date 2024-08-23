# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: PatchAppTableFormFieldRequest = PatchAppTableFormFieldRequest.builder() \
		.app_token("bascnCMII2ORej2RItqpZZUNMIe") \
		.table_id("tblsRc9GRRXKqhvW") \
		.form_id("vewTpR1urY") \
		.field_id("fldjX7dUj5") \
		.request_body(AppTableFormPatchedField.builder()
					  .pre_field_id("str")
					  .title("str")
					  .description("str")
					  .required(bool)
					  .visible(bool)
					  .build()) \
		.build()

	# 发起请求
	response: PatchAppTableFormFieldResponse = client.bitable.v1.app_table_form_field.patch(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_form_field.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: PatchAppTableFormFieldRequest = PatchAppTableFormFieldRequest.builder() \
		.app_token("bascnCMII2ORej2RItqpZZUNMIe") \
		.table_id("tblsRc9GRRXKqhvW") \
		.form_id("vewTpR1urY") \
		.field_id("fldjX7dUj5") \
		.request_body(AppTableFormPatchedField.builder()
					  .pre_field_id("str")
					  .title("str")
					  .description("str")
					  .required(bool)
					  .visible(bool)
					  .build()) \
		.build()

	# 发起请求
	response: PatchAppTableFormFieldResponse = await client.bitable.v1.app_table_form_field.apatch(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_form_field.apatch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
