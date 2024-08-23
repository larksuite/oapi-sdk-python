# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.corehr.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: DeleteWorkingHoursTypeRequest = DeleteWorkingHoursTypeRequest.builder() \
		.working_hours_type_id("325325254") \
		.build()

	# 发起请求
	response: DeleteWorkingHoursTypeResponse = client.corehr.v1.working_hours_type.delete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.working_hours_type.delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: DeleteWorkingHoursTypeRequest = DeleteWorkingHoursTypeRequest.builder() \
		.working_hours_type_id("325325254") \
		.build()

	# 发起请求
	response: DeleteWorkingHoursTypeResponse = await client.corehr.v1.working_hours_type.adelete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v1.working_hours_type.adelete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
