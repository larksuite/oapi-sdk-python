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
	request: UpdateProgressEcoBackgroundCheckRequest = UpdateProgressEcoBackgroundCheckRequest.builder() \
		.request_body(UpdateProgressEcoBackgroundCheckRequestBody.builder()
					  .background_check_id("6931286400470354183")
					  .stage_id("6931286400470354183")
					  .stage_en_name("stage report")
					  .stage_name("阶段报告")
					  .stage_time("1660123456789")
					  .result("通过")
					  .report_file_list([])
					  .build()) \
		.build()

	# 发起请求
	response: UpdateProgressEcoBackgroundCheckResponse = client.hire.v1.eco_background_check.update_progress(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.eco_background_check.update_progress failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: UpdateProgressEcoBackgroundCheckRequest = UpdateProgressEcoBackgroundCheckRequest.builder() \
		.request_body(UpdateProgressEcoBackgroundCheckRequestBody.builder()
					  .background_check_id("6931286400470354183")
					  .stage_id("6931286400470354183")
					  .stage_en_name("stage report")
					  .stage_name("阶段报告")
					  .stage_time("1660123456789")
					  .result("通过")
					  .report_file_list([])
					  .build()) \
		.build()

	# 发起请求
	response: UpdateProgressEcoBackgroundCheckResponse = await client.hire.v1.eco_background_check.aupdate_progress(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.hire.v1.eco_background_check.aupdate_progress failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
