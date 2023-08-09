# Code generated by Lark OpenAPI.

import lark_oapi as lark
from lark_oapi.api.baike.v1 import *


def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(lark.APP_ID) \
        .app_secret(lark.APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ExtractEntityRequest = ExtractEntityRequest.builder() \
        .request_body(ExtractEntityRequestBody.builder()
                      .text("企业百科是一部高效汇聚企业内各类信息，并可由企业成员参与编辑的在线百科全书")
                      .build()) \
        .build()

    # 发起请求
    response: ExtractEntityResponse = client.baike.v1.entity.extract(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.baike.v1.entity.extract failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()