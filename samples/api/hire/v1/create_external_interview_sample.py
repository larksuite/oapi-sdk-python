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
	request: CreateExternalInterviewRequest = CreateExternalInterviewRequest.builder() \
		.request_body(ExternalInterview.builder()
					  .external_id("123")
					  .external_application_id("6960663240925956437")
					  .participate_status(1)
					  .begin_time(1618500278638)
					  .end_time(1618500278639)
					  .interview_assessments([])
					  .build()) \
		.build()

	# 发起请求
	response: CreateExternalInterviewResponse = client.hire.v1.external_interview.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.external_interview.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CreateExternalInterviewRequest = CreateExternalInterviewRequest.builder() \
		.request_body(ExternalInterview.builder()
					  .external_id("123")
					  .external_application_id("6960663240925956437")
					  .participate_status(1)
					  .begin_time(1618500278638)
					  .end_time(1618500278639)
					  .interview_assessments([])
					  .build()) \
		.build()

	# 发起请求
	response: CreateExternalInterviewResponse = await client.hire.v1.external_interview.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.external_interview.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
