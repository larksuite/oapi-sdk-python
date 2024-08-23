# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.corehr.v2 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: DeleteProbationAssessmentRequest = DeleteProbationAssessmentRequest.builder() \
		.assessment_id("7140964208476371331") \
		.build()

	# 发起请求
	response: DeleteProbationAssessmentResponse = client.corehr.v2.probation_assessment.delete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v2.probation_assessment.delete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: DeleteProbationAssessmentRequest = DeleteProbationAssessmentRequest.builder() \
		.assessment_id("7140964208476371331") \
		.build()

	# 发起请求
	response: DeleteProbationAssessmentResponse = await client.corehr.v2.probation_assessment.adelete(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.corehr.v2.probation_assessment.adelete failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
