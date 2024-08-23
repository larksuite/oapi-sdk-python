# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.vc.v1 import *


def main():
	# 创建client
	client = lark.Client.builder() \
		.app_id(lark.APP_ID) \
		.app_secret(lark.APP_SECRET) \
		.log_level(lark.LogLevel.DEBUG) \
		.build()

	# 构造请求对象
	request: GetResourceReservationListRequest = GetResourceReservationListRequest.builder() \
		.room_level_id("omb_57c9cc7d9a81e27e54c8fabfd02759e7") \
		.need_topic(True) \
		.start_time("1655276858") \
		.end_time("1655276858") \
		.room_ids([]) \
		.is_exclude(False) \
		.page_size(20) \
		.page_token("str") \
		.build()

	# 发起请求
	response: GetResourceReservationListResponse = client.vc.v1.resource_reservation_list.get(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.vc.v1.resource_reservation_list.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
	request: GetResourceReservationListRequest = GetResourceReservationListRequest.builder() \
		.room_level_id("omb_57c9cc7d9a81e27e54c8fabfd02759e7") \
		.need_topic(True) \
		.start_time("1655276858") \
		.end_time("1655276858") \
		.room_ids([]) \
		.is_exclude(False) \
		.page_size(20) \
		.page_token("str") \
		.build()

	# 发起请求
	response: GetResourceReservationListResponse = await client.vc.v1.resource_reservation_list.aget(request)

	# 处理失败返回
	if not response.success():
		lark.logger.error(
			f"client.vc.v1.resource_reservation_list.aget failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
		return

	# 处理业务结果
	lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
	# asyncio.run(amain()) 异步方式
	main()
