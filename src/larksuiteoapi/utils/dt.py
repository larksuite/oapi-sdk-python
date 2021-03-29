# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy
from typing import List, TypeVar

import attr

T = TypeVar('T')

int_to_string_fields = "__int_to_string_fields__"


def to_json(data):
    od = data.__dict__
    d = {}
    attr_field = attr.fields(data.__class__)
    for att in getattr(data, '__attrs_attrs__', []):
        att_name = att.name
        if att_name == int_to_string_fields:
            continue
        json_name = getattr(attr_field, att.name).metadata.get('json') or att_name
        v = od.get(att.name, att.default)
        if hasattr(v, 'json'):
            d[json_name] = v.json()
        elif isinstance(v, list):
            d[json_name] = [to_json(i) for i in v]
        elif isinstance(v, dict):
            d[json_name] = {kk: to_json(vv) for kk, vv in v.items()}
        elif att_name in od.get(int_to_string_fields, []):
            if v is None:
                d[json_name] = None
            else:
                d[json_name] = str(v)
        else:
            d[json_name] = v
    return d


def to_json_decorator(cls):
    cls.json = to_json
    return cls


def make_datatype(t, kwargs):
    """make_datatype

    :type t: Type[T]
    :type kwargs: Any
    :rtype: T
    """
    if not kwargs:
        return
    kwargs = deepcopy(kwargs)

    if isinstance(kwargs, (int, str, bool)):
        return kwargs

    if t.__class__ == List.__class__ and isinstance(kwargs, list):
        return [make_datatype(t.__args__[0], i) for i in kwargs]

    if not hasattr(t, '__attrs_attrs__'):
        return kwargs

    d = {}
    attr_field = attr.fields(t)
    for att in getattr(t, '__attrs_attrs__', []):
        att_name = att.name
        json_name = getattr(attr_field, att.name).metadata.get('json') or att_name
        att_default = att.default

        att_value = kwargs.get(json_name)
        if att_value:
            d[att_name] = make_datatype(att.type, att_value)
            del kwargs[json_name]
        elif att_default is attr.NOTHING:
            d[att_name] = None

    return t(**d)


def int_convert_bool(v):
    return bool(v)


def to_lower_converter(s):
    if isinstance(s, str):
        return s.lower()
    return s
