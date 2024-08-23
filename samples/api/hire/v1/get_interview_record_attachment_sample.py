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
	request: GetInterviewRecordAttachmentRequest = GetInterviewRecordAttachmentRequest.builder() \
		.application_id("6949805467799537964") \
		.interview_record_id("6969137186734393644") \
		.language(1) \
		.build()

	# 发起请求
	response: GetInterviewRecordAttachmentResponse = client.hire.v1.interview_record_attachment.get(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.interview_record_attachment.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: GetInterviewRecordAttachmentRequest = GetInterviewRecordAttachmentRequest.builder() \
		.application_id("6949805467799537964") \
		.interview_record_id("6969137186734393644") \
		.language(1) \
		.build()

	# 发起请求
	response: GetInterviewRecordAttachmentResponse = await client.hire.v1.interview_record_attachment.aget(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.interview_record_attachment.aget failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
