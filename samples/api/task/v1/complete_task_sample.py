# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.task.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: CompleteTaskRequest = CompleteTaskRequest.builder() \
		.task_id("bb54ab99-d360-434f-bcaa-a4cc4c05840e") \
		.build()

	# 发起请求
	response: CompleteTaskResponse = client.task.v1.task.complete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.task.v1.task.complete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CompleteTaskRequest = CompleteTaskRequest.builder() \
		.task_id("bb54ab99-d360-434f-bcaa-a4cc4c05840e") \
		.build()

	# 发起请求
	response: CompleteTaskResponse = await client.task.v1.task.acomplete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.task.v1.task.acomplete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
