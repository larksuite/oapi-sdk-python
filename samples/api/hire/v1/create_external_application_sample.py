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
	request: CreateExternalApplicationRequest = CreateExternalApplicationRequest.builder() \
		.request_body(ExternalApplication.builder()
					  .external_id("123")
					  .job_recruitment_type(1)
					  .job_title("高级Java")
					  .resume_source("lagou")
					  .stage("1")
					  .talent_id("6960663240925956459")
					  .termination_reason("不合适")
					  .delivery_type(1)
					  .modify_time(1618500278645)
					  .create_time(1618500278644)
					  .termination_type("health")
					  .build()) \
		.build()

	# 发起请求
	response: CreateExternalApplicationResponse = client.hire.v1.external_application.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.external_application.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CreateExternalApplicationRequest = CreateExternalApplicationRequest.builder() \
		.request_body(ExternalApplication.builder()
					  .external_id("123")
					  .job_recruitment_type(1)
					  .job_title("高级Java")
					  .resume_source("lagou")
					  .stage("1")
					  .talent_id("6960663240925956459")
					  .termination_reason("不合适")
					  .delivery_type(1)
					  .modify_time(1618500278645)
					  .create_time(1618500278644)
					  .termination_type("health")
					  .build()) \
		.build()

	# 发起请求
	response: CreateExternalApplicationResponse = await client.hire.v1.external_application.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.external_application.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
