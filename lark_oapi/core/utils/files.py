import io
from email.message import Message
from email.policy import default
from typing import Any, Dict, Optional

from lark_oapi.core import Content_Disposition


class Files(object):
    @staticmethod
    def parse_file_name(headers: Dict[str, str]) -> Optional[str]:
        content_disposition = headers.get(Content_Disposition)
        if content_disposition is None:
            return None

        message = Message(policy=default)
        message[Content_Disposition] = content_disposition

        params = dict(message.get_params(header=Content_Disposition, unquote=True))

        file_name = params.get("filename")
        if file_name is not None:
            return file_name.encode('ISO-8859-1').decode()
        return None

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
