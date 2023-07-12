import cgi
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
    def parse_form_data(obj: Any) -> Dict[str, str]:
        if not hasattr(obj, "__dict__"):
            return {}
        d = vars(obj)
        for k, v in d.items():
            if k == "file" or v is None:
                continue
            d[k] = str(v)

        return d
