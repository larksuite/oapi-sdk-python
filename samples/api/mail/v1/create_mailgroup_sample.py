# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.mail.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: CreateMailgroupRequest = CreateMailgroupRequest.builder() \
		.request_body(Mailgroup.builder()
					  .email("test_mail_group@xxx.xx")
					  .name("test mail group")
					  .description("mail group for testing")
					  .who_can_send_mail("ALL_INTERNAL_USERS")
					  .build()) \
		.build()

	# 发起请求
	response: CreateMailgroupResponse = client.mail.v1.mailgroup.create(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.mail.v1.mailgroup.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: CreateMailgroupRequest = CreateMailgroupRequest.builder() \
		.request_body(Mailgroup.builder()
					  .email("test_mail_group@xxx.xx")
					  .name("test mail group")
					  .description("mail group for testing")
					  .who_can_send_mail("ALL_INTERNAL_USERS")
					  .build()) \
		.build()

	# 发起请求
	response: CreateMailgroupResponse = await client.mail.v1.mailgroup.acreate(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.mail.v1.mailgroup.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
