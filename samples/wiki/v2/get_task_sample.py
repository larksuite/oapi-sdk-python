# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *


def main():
	# 构建client
	client = lark.Client.builder() \
		.app_id("APP_ID") \
		.app_secret("APP_SECRET") \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: GetTaskRequest = lark.wiki.v2.GetTaskRequest.builder() \
		.task_id("7037044037068177428-075c9481e6a0007c1df689dfbe5b55a08b6b06f7") \
		.task_type("move") \
		.build()

	# 发起请求
	response: GetTaskResponse = client.wiki.v2.task.get(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.wiki.v2.task.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	main()