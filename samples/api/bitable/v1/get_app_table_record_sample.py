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
	request: GetAppTableRecordRequest = GetAppTableRecordRequest.builder() \
		.app_token("bascnCMII2ORej2RItqpZZUNMIe") \
		.table_id("tblxI2tWaxP5dG7p") \
		.record_id("recn0hoyXL") \
		.text_field_as_array(True) \
		.user_id_type("user_id") \
		.display_formula_ref(True) \
		.with_shared_url(bool) \
		.automatic_fields(True) \
		.build()

	# 发起请求
	response: GetAppTableRecordResponse = client.bitable.v1.app_table_record.get(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_record.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: GetAppTableRecordRequest = GetAppTableRecordRequest.builder() \
		.app_token("bascnCMII2ORej2RItqpZZUNMIe") \
		.table_id("tblxI2tWaxP5dG7p") \
		.record_id("recn0hoyXL") \
		.text_field_as_array(True) \
		.user_id_type("user_id") \
		.display_formula_ref(True) \
		.with_shared_url(bool) \
		.automatic_fields(True) \
		.build()

	# 发起请求
	response: GetAppTableRecordResponse = await client.bitable.v1.app_table_record.aget(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.bitable.v1.app_table_record.aget failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
