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
    request: CreateCompanyRequest = CreateCompanyRequest.builder() \
        .client_token("12454646") \
        .request_body(Company.builder()
                      .hiberarchy_common(HiberarchyCommon.builder().build())
                      .type(Enum.builder().build())
                      .industry_list([])
                      .legal_representative([])
                      .post_code("邮编")
                      .tax_payer_id("123456840")
                      .confidential(True)
                      .sub_type_list([])
                      .branch_company(True)
                      .primary_manager([])
                      .custom_fields([])
                      .currency(Currency.builder().build())
                      .phone(PhoneNumberAndAreaCode.builder().build())
                      .fax(PhoneNumberAndAreaCode.builder().build())
                      .registered_office_address_info(Address.builder().build())
                      .office_address_info(Address.builder().build())
                      .build()) \
        .build()

    # 发起请求
    response: CreateCompanyResponse = client.corehr.v1.company.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.corehr.v1.company.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
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
    request: CreateCompanyRequest = CreateCompanyRequest.builder() \
        .client_token("12454646") \
        .request_body(Company.builder()
                      .hiberarchy_common(HiberarchyCommon.builder().build())
                      .type(Enum.builder().build())
                      .industry_list([])
                      .legal_representative([])
                      .post_code("邮编")
                      .tax_payer_id("123456840")
                      .confidential(True)
                      .sub_type_list([])
                      .branch_company(True)
                      .primary_manager([])
                      .custom_fields([])
                      .currency(Currency.builder().build())
                      .phone(PhoneNumberAndAreaCode.builder().build())
                      .fax(PhoneNumberAndAreaCode.builder().build())
                      .registered_office_address_info(Address.builder().build())
                      .office_address_info(Address.builder().build())
                      .build()) \
        .build()

    # 发起请求
    response: CreateCompanyResponse = await client.corehr.v1.company.acreate(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.corehr.v1.company.acreate failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    # asyncio.run(amain()) 异步方式
    main()
