# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.search.v2 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: CreateAppRequest = CreateAppRequest.builder() \
		.user_id_type("user_id") \
		.page_size(20) \
		.page_token("str") \
		.request_body(CreateAppRequestBody.builder()
					  .query("测试应用")
					  .build()) \
		.build()

	# 发起请求
	response: CreateAppResponse = client.search.v2.app.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.search.v2.app.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CreateAppRequest = CreateAppRequest.builder() \
		.user_id_type("user_id") \
		.page_size(20) \
		.page_token("str") \
		.request_body(CreateAppRequestBody.builder()
					  .query("测试应用")
					  .build()) \
		.build()

	# 发起请求
	response: CreateAppResponse = await client.search.v2.app.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.search.v2.app.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
