# -*- coding: UTF-8 -*-

from larksuiteoapi.service.drive_explorer.v2 import Service as DriveExplorerV2Service, model as drive_explorer_v2_model
from larksuiteoapi.service.sheets.v2 import Service as SheetsV2Service, model as sheets_v2_model
from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from larksuiteoapi import DOMAIN_FEISHU, DOMAIN_LARK_SUITE, Config, LEVEL_DEBUG

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
# conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)

# for memory store and logger(level=debug)
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)


def test_create_sheets():
    driveExplorerV2Service = DriveExplorerV2Service(conf)
    # get my root folder
    resp = driveExplorerV2Service.folders.root_meta().do()
    print('get my root folder request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)
        return
    folderRootMetaResult = resp.data

    # create sheets file
    fileCreateReqBody = drive_explorer_v2_model.FileCreateReqBody()
    fileCreateReqBody.type = 'sheet'
    fileCreateReqBody.title = 'test'
    resp = driveExplorerV2Service.files.create(fileCreateReqBody).set_folderToken(folderRootMetaResult.token).do()
    print('create sheets request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        # FileCreateResult(url='https://test-c5pc78flqk06.feishu.cn/sheets/shtcnx33qSL4xqk23jl9gX6uhjc', revision=None, token='shtcnx33qSL4xqk23jl9gX6uhjc')
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)
        return
    fileCreateResult = resp.data
    sheetsToken = fileCreateResult.token
    # create sheet(test_sheet)
    sheetsV2Service = SheetsV2Service(conf)
    spreadsheetsSheetsBatchUpdateReqBody = sheets_v2_model.SpreadsheetsSheetsBatchUpdateReqBody()
    request = sheets_v2_model.Request(
        add_sheet=sheets_v2_model.AddSheet(properties=sheets_v2_model.Properties(title="test_sheet")))
    spreadsheetsSheetsBatchUpdateReqBody.requests = [request]

    resp = sheetsV2Service.spreadsheetss.sheets_batch_update(spreadsheetsSheetsBatchUpdateReqBody) \
        .set_spreadsheetToken(sheetsToken).do()
    print('create sheet request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        # SpreadsheetsSheetsBatchUpdateResult(replies=[{'addSheet': {'properties': {'sheetId': '4AnzPi', 'title': 'test_sheet'}}}])
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)
        return
    sheetId = resp.data.replies[0].add_sheet.properties.sheet_id
    # insert data
    spreadsheetsValuesPrependReqBody = sheets_v2_model.SpreadsheetsValuesPrependReqBody(
        value_range=sheets_v2_model.ValueRange(range=sheetId + '!A1:C1', values=[[1, 2, '3']]))
    resp = sheetsV2Service.spreadsheetss.values_prepend(spreadsheetsValuesPrependReqBody).set_spreadsheetToken(sheetsToken).do()
    print('insert data request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        # SpreadsheetsSheetsBatchUpdateResult(replies=[Reply(update_sheet=None, add_sheet=AddSheet(properties=Properties(sheet_id='4g1iWQ', title='test_sheet', index=None, hidden=None, frozen_row_count=None, frozen_col_count=None, protect=None)), copy_sheet=None, delete_sheet=None)])
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)
        return


if __name__ == '__main__':
    test_create_sheets()
