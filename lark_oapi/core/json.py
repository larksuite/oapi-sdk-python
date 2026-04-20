import base64
import copy
import datetime
import io
from json import *
from typing import *

from .const import UTF_8
from .type import T


class JSON(object):

    @staticmethod
    def marshal(obj: Any, indent=None) -> Optional[str]:
        if obj is None:
            return None
        return dumps(obj, cls=Encoder, indent=indent, ensure_ascii=False)

    @staticmethod
    def unmarshal(json_str: str, clazz: Type[T]) -> T:
        dict_obj = loads(json_str)
        return clazz(dict_obj)


class Encoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, io.BufferedReader):
            return o.__str__()
        if hasattr(o, "__dict__"):
            return filter_null(copy.deepcopy(vars(o)))
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, bytes):
            # Try UTF-8 first (the common case for wire payloads that
            # happen to be stringly-typed), but fall back to base64 for
            # genuine binary data (JPEG/PNG/PDF bytes pulled out of a
            # download response that is later JSON-serialized by caller
            # code). Without this fallback, any non-UTF-8 byte sequence
            # raises ``UnicodeDecodeError`` mid-marshal and the whole
            # response is lost.
            try:
                return str(o, encoding=UTF_8)
            except UnicodeDecodeError:
                return base64.b64encode(o).decode("ascii")
        if isinstance(o, int):
            return int(o)
        if isinstance(o, float):
            return float(o)
        if isinstance(o, set):
            return list(o)
        return super().default(o)


def filter_null(d: Dict) -> Dict:
    if isinstance(d, dict):
        for k, v in list(d.items()):
            if isinstance(v, dict):
                filter_null(v)
            elif v is None:
                del d[k]

    return d
