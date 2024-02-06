# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.sheets.v3 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: GetSpreadsheetSheetFloatImageRequest = GetSpreadsheetSheetFloatImageRequest.builder() \
        .spreadsheet_token("shtcnmBA*****yGehy8") \
        .sheet_id("0b**12") \
        .float_image_id("ye06SS14ph") \
        .build()

    # 发起请求
    response: GetSpreadsheetSheetFloatImageResponse = client.sheets.v3.spreadsheet_sheet_float_image.get(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.sheets.v3.spreadsheet_sheet_float_image.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: GetSpreadsheetSheetFloatImageRequest = GetSpreadsheetSheetFloatImageRequest.builder() \
        .spreadsheet_token("shtcnmBA*****yGehy8") \
        .sheet_id("0b**12") \
        .float_image_id("ye06SS14ph") \
        .build()

    # 发起请求
    response: GetSpreadsheetSheetFloatImageResponse = await client.sheets.v3.spreadsheet_sheet_float_image.aget(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.sheets.v3.spreadsheet_sheet_float_image.aget failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()