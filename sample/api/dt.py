import attr
import json
import time
from typing import List, Any
from larksuiteoapi.utils.dt import to_json_decorator, make_datatype


@to_json_decorator
@attr.s
class AvatarInfo(object):
    avatar_72 = attr.ib(type=str, default=None, metadata={'json': 'avatar_72'})
    avatar_240 = attr.ib(type=str, default=None)
    avatar_640 = attr.ib(type=str, default=None)
    avatar_origin = attr.ib(type=str, default=None)


@to_json_decorator
@attr.s
class User(object):
    __int_to_string_fields__ = attr.ib(type=List[str], default=["id"])
    id = attr.ib(type=int, default=None, metadata={'json': 'id'})
    age = attr.ib(type=int, default=None, metadata={'json': 'age'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    en_name = attr.ib(type=str, default=None, metadata={'json': 'en_name'})
    avatar = attr.ib(type=AvatarInfo, default=None, metadata={'json': 'avatar'})
    finds = attr.ib(type=List[str], default=None, metadata={'json': 'finds'})


@to_json_decorator
@attr.s
class UserUpdateResult(object):
    user = attr.ib(type=User, default=None)


def test_user_update():
    d = json.loads(
        '{"id": "9223372036854775806", "age":0, "name": "","finds":["1"] , "avatar":{"avatar_72":"avatar_72-1"}, "en_name":null }')
    user = make_datatype(User, d)
    print(user)


@to_json_decorator
@attr.s
class ValueRange(object):
    major_dimension = attr.ib(type=str, default=None, metadata={'json': 'majorDimension'})
    range = attr.ib(type=str, default=None, metadata={'json': 'range'})
    revision = attr.ib(type=int, default=None, metadata={'json': 'revision'})
    values = attr.ib(type=List[List[Any]], default=None, metadata={'json': 'values'})


@attr.s
class SpreadsheetsValuesGetResult(object):
    revision = attr.ib(type=int, default=None, metadata={'json': 'revision'})
    spreadsheet_token = attr.ib(type=str, default=None, metadata={'json': 'spreadsheetToken'})
    value_range = attr.ib(type=ValueRange, default=None, metadata={'json': 'valueRange'})


def test_spreadsheetsValuesGetResult():
    d = json.loads(
        '{"revision":0,"spreadsheetToken":"***","valueRange":{"majorDimension":"ROWS","range":"***","revision":0,"values":[["***", true, 1, 0.01]]}}')
    spreadsheetsValuesGetResult = make_datatype(SpreadsheetsValuesGetResult, d)
    print(spreadsheetsValuesGetResult)


if __name__ == '__main__':
    # test_user_update()
    test_spreadsheetsValuesGetResult()
