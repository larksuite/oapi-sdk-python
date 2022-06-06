# -*- coding: UTF-8 -*-
from larksuiteoapi import DOMAIN_FEISHU, Config, LEVEL_DEBUG
from larksuiteoapi.service.docx.v1 import Service as DocxService, model

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key）。
# 更多介绍请看：Github->README.zh.md->如何构建应用配置（AppSettings）
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Error级别）
# 更多介绍请看：Github->README.zh.md->如何构建整体配置（Config）
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)

service = DocxService(conf)


def test_create_doc():
    # body
    body = model.DocumentCreateReqBody()
    body.folder_token = 'fldcniHf40Vcv1DoEc8SXeuA0Zd'
    body.title = 'document-python'
    req_call = service.documents.create(body, None, 'u-12kPy7i1Zf3Xg6YBJaoncNgk2cmBk1AFiww0lkC8G9SO')
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_get_doc():
    req_call = service.documents.get(None, 'u-WKCn2nuMHEgeTQ9YyuFeMg')
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_get_raw_doc():
    req_call = service.documents.raw_content(None, 'u-12kPy7i1Zf3Xg6YBJaoncNgk2cmBk1AFiww0lkC8G9SO')
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_list_blocks():
    req_call = service.document_blocks.list(None, 'u-12kPy7i1Zf3Xg6YBJaoncNgk2cmBk1AFiww0lkC8G9SO')
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    req_call.set_page_size(100)
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_create_blocks():
    body = model.DocumentBlockChildrenCreateReqBody()
    body.index = 0

    block = model.Block()
    block.block_type = 2

    text = model.Text()
    e = model.TextElement()
    run = model.TextRun()
    run.content = "66666"
    style = model.TextElementStyle()
    style.background_color = 14
    style.text_color = 5
    run.text_element_style = style
    e.text_run = run

    es = [e]
    text.elements = es
    block.text = text
    bs = [block]
    body.children = bs

    req_call = service.document_block_childrens.create(body, None, 'u-12kPy7i1Zf3Xg6YBJaoncNgk2cmBk1AFiww0lkC8G9SO')
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    req_call.set_block_id("doxcnKIaoQecc6GWwozvApH6rOf")

    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_update_blocks():
    req = model.UpdateBlockRequest()

    text = model.Text()
    e = model.TextElement()
    run = model.TextRun()
    run.content = "8888"
    style = model.TextElementStyle()
    style.background_color = 14
    style.text_color = 5
    run.text_element_style = style
    e.text_run = run

    es = [e]
    text.elements = es
    r = model.UpdateTextElementsRequest()
    r.elements = es
    req.update_text_elements = r

    req_call = service.document_blocks.patch(req, None, 'u-03ETXnQCx2bGzlCpiLkBxA0k0Yr5k1C9XwG001a00csd')
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    req_call.set_block_id("doxcnKIaoQecc6GWwozvApH6rOf")

    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


def test_list_sub_blocks():
    req_call = service.document_block_childrens.get(None, 'u-12kPy7i1Zf3Xg6YBJaoncNgk2cmBk1AFiww0lkC8G9SO',None)
    req_call.set_document_id("doxcnEldNqtJ9Og88tf6dnVVNNf")
    req_call.set_block_id("doxcnKIaoQecc6GWwozvApH6rOf")
    req_call.set_page_size(100)
    resp = req_call.do()
    print('request id = %s' % resp.get_request_id())
    print('http status code = %s' % resp.get_http_status_code())
    print('header = %s' % resp.get_header().items())
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)

if __name__ == '__main__':
    # test_create_doc()
    test_get_doc()
    # test_get_raw_doc()
    #test_list_blocks()
    #test_create_blocks()
    #test_list_sub_blocks()
    #test_update_blocks()
