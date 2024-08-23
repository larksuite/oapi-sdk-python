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
	request: ListDepartmentRequest = ListDepartmentRequest.builder() \
		.user_id_type("open_id") \
		.department_id_type("open_department_id") \
		.parent_department_id("od-80884c92e43e") \
		.fetch_child(False) \
		.page_size(10) \
		.page_token("5bc498db4617") \
		.build()

	# 发起请求
	response: ListDepartmentResponse = client.contact.v3.department.list(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.contact.v3.department.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: ListDepartmentRequest = ListDepartmentRequest.builder() \
		.user_id_type("open_id") \
		.department_id_type("open_department_id") \
		.parent_department_id("od-80884c92e43e") \
		.fetch_child(False) \
		.page_size(10) \
		.page_token("5bc498db4617") \
		.build()

	# 发起请求
	response: ListDepartmentResponse = await client.contact.v3.department.alist(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.contact.v3.department.alist failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
