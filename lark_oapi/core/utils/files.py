import io
import os
from email.utils import decode_rfc2231
from typing import Any, Dict, Optional
from urllib.parse import unquote

from lark_oapi.core import Content_Disposition


class Files(object):
    @staticmethod
    def parse_file_name(headers: Dict[str, str]) -> Optional[str]:
        content_disposition = headers.get(Content_Disposition)
        if content_disposition is None:
            return None

        parts = content_disposition.split(';')
        params = {}

        for part in parts:
            if '=' in part:
                k, v = part.strip().split('=', 1)
                params[k] = v.strip(' "')

        if 'filename*' in params:
            # Decode RFC2231 encoded format
            filename = decode_rfc2231(params['filename*'])[2]
            filename = unquote(filename)
        elif 'filename' in params:
            # Handle possible encoding issues with a basic unquote
            filename = unquote(params['filename'])
            # or try to decode using utf-8 if it seems like a valid utf-8 string
            try:
                filename = filename.encode('latin1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        else:
            filename = None

        return filename

    @staticmethod
    def parse_form_data(obj: Any) -> Dict[str, Any]:
        fd = {}
        if isinstance(obj, dict):
            fd = dict(obj)
        elif not hasattr(obj, "__dict__"):
            return fd
        else:
            fd = dict(vars(obj))

        for k, v in fd.items():
            if isinstance(v, (io.IOBase, tuple)):
                fd[k] = Files._file_value(obj, k, v)
                continue
            if v is None:
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
                if isinstance(v, (io.IOBase, tuple)):
                    files[k] = Files._file_value(obj, k, v)
                    to_del_keys.append(k)
            for k in to_del_keys:
                del obj[k]
        elif not hasattr(obj, "__dict__"):
            return None
        else:
            for k, v in vars(obj).items():
                if isinstance(v, (io.IOBase, tuple)):
                    files[k] = Files._file_value(obj, k, v)
                    setattr(obj, k, None)

        return files

    @staticmethod
    def _file_value(obj: Any, field: str, value: Any):
        """Normalize filenames while retaining the stream and tuple MIME/headers."""
        filename_field = getattr(obj, "_file_names", {}).get(field)
        filename = getattr(obj, filename_field, None) if filename_field else None
        if filename is not None and not isinstance(filename, str):
            raise ValueError("upload filename must be a string")
        if filename:
            if filename in (".", "..") or any(c in filename for c in "/\\\r\n\x00"):
                raise ValueError("upload filename must not contain paths or control characters")
            if isinstance(value, tuple):
                return (filename,) + value[1:]
            return (filename, value)
        if isinstance(value, tuple):
            return value
        name = getattr(value, "name", None)
        filename = os.path.basename(name) if isinstance(name, str) else "upload"
        return (filename or "upload", value)
