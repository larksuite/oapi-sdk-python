# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.aily.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: ListAilySessionAilyMessageRequest = ListAilySessionAilyMessageRequest.builder() \
		.aily_session_id("session_4dfunz7sp1g8m") \
		.page_size(int) \
		.page_token("str") \
		.run_id("run_4dfrxvctjqzzj") \
		.with_partial_message(False) \
		.build()

	# 发起请求
	response: ListAilySessionAilyMessageResponse = client.aily.v1.aily_session_aily_message.list(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.aily.v1.aily_session_aily_message.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: ListAilySessionAilyMessageRequest = ListAilySessionAilyMessageRequest.builder() \
		.aily_session_id("session_4dfunz7sp1g8m") \
		.page_size(int) \
		.page_token("str") \
		.run_id("run_4dfrxvctjqzzj") \
		.with_partial_message(False) \
		.build()

	# 发起请求
	response: ListAilySessionAilyMessageResponse = await client.aily.v1.aily_session_aily_message.alist(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.aily.v1.aily_session_aily_message.alist failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
