# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.approval.v4 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: ListInstanceRequest = ListInstanceRequest.builder() \
		.page_size(100) \
		.page_token("nF1ZXJ5VGhlbkZldGNoCgAAAAAA6PZwFmUzSldvTC1yU") \
		.approval_code("7C468A54-8745-2245-9675-08B7C63E7A85") \
		.start_time("1567690398020") \
		.end_time("1567690398020") \
		.build()

	# 发起请求
	response: ListInstanceResponse = client.approval.v4.instance.list(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.approval.v4.instance.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: ListInstanceRequest = ListInstanceRequest.builder() \
		.page_size(100) \
		.page_token("nF1ZXJ5VGhlbkZldGNoCgAAAAAA6PZwFmUzSldvTC1yU") \
		.approval_code("7C468A54-8745-2245-9675-08B7C63E7A85") \
		.start_time("1567690398020") \
		.end_time("1567690398020") \
		.build()

	# 发起请求
	response: ListInstanceResponse = await client.approval.v4.instance.alist(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.approval.v4.instance.alist failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
