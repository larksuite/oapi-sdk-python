# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.im.v1 import *


def main():
	# 构建client
	client = lark.Client.builder() \
		.app_id("APP_ID") \
		.app_secret("APP_SECRET") \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: ReadUsersMessageRequest = lark.im.v1.ReadUsersMessageRequest.builder() \
		.message_id("om_dc13264520392913993dd051dba21dcf") \
		.user_id_type("user_id") \
		.page_size(20) \
		.page_token("GxmvlNRvP0NdQZpa7yIqf_Lv_QuBwTQ8tXkX7w-irAghVD_TvuYd1aoJ1LQph86O-XImC4X9j9FhUPhXQDvtrQ==") \
		.build()

	# 发起请求
	response: ReadUsersMessageResponse = client.im.v1.message.read_users(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.im.v1.message.read_users failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	main()