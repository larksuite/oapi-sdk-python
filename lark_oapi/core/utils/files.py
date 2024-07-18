import cgi
import io
from typing import Any, Dict, Optional

from lark_oapi.core import Content_Disposition


class Files(object):
    @staticmethod
    def parse_file_name(headers: Dict[str, str]) -> Optional[str]:
        media_type = headers.get(Content_Disposition)
        if media_type is None:
            return None
        _, params = cgi.parse_header(media_type)
        file_name = params["filename"]
        return file_name.encode('ISO-8859-1').decode()

    @staticmethod
    def parse_form_data(obj: Any) -> Dict[str, Any]:
        fd = {}
        if isinstance(obj, dict):
            fd = obj
        elif not hasattr(obj, "__dict__"):
            return fd
        else:
            fd = vars(obj)

        for k, v in fd.items():
            if v is None or isinstance(v, io.IOBase) or isinstance(v, tuple):
                continue
            fd[k] = str(v)

        return fd

    @staticmethod
    def extract_files(obj: Any):
        if obj is None:
            return None
        files = {}
        if isinstance(obj, dict):
            to_del_keys = []
            for k, v in obj.items():
                if isinstance(v, io.IOBase):
                    files[k] = v
                    to_del_keys.append(k)
            for k in to_del_keys:
                del obj[k]
        elif not hasattr(obj, "__dict__"):
            return None
        else:
            for k, v in vars(obj).items():
                if isinstance(v, io.IOBase):
                    files[k] = v
                    setattr(obj, k, None)

        return files
