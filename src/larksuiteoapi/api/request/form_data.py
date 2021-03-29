# -*- coding: UTF-8 -*-
import os
import tempfile
from typing import IO, Any, Dict, List, Tuple, Union


class FormDataFile(object):
    def __init__(self, content, file_name='unkown', mime_type=''):
        # type: (Union[bytes, IO[Any]], str, str) -> None
        self.name = file_name
        self.type = mime_type
        self.content = content
        self.file_path = None
        self.__prepared = False  # type: bool
        self.field_name = ''  # type: str

    def prepare(self):
        if self.__prepared:
            return
        tmp_file_path = tempfile.mktemp('.larksuiteoapisdk')
        current_file = self.content  # type: Union[IO[Any], bytes]
        tmp_file = open(tmp_file_path, 'wb')
        if isinstance(current_file, bytes):
            current_file_bytes = current_file
            tmp_file.write(current_file_bytes)
        else:
            for content in current_file:
                tmp_file.write(content)
        tmp_file.flush()
        tmp_file.close()
        self.file_path = tmp_file_path
        self.__prepared = True

    def delete(self):
        if self.file_path:
            os.remove(self.file_path)


class FormData(object):
    def __init__(self, files=None, params=None):
        # type: (Union[None, List[FormDataFile]], Union[None, Dict[str, Union[bytes, str]]]) -> None
        if files is None:
            files = []
        if params is None:
            params = {}
        self.files = files
        self.params = params

    def __str__(self):
        return "params:%s, file count:%s" % (self.params, len(self.files))

    def to_map(self):
        # type: () -> Tuple[List[Tuple[str, Tuple[str, IO, str]]], Dict[str, str], List[IO]]

        ret_files = []  # type: List[Tuple[str, Tuple[str, Union[bytes, IO], str]]]
        ret_data = {}  # type: Dict[str, Union[bytes, str]]
        need_close = []  # type: List[IO[Any]]

        for file in self.files:
            content = file.content
            if file.file_path is not None:
                content = open(file.file_path, 'rb')
                need_close += [content]
            if content is None:
                continue
            if file.type != '':
                f = (file.field_name, (file.name, content, file.type))
            else:
                f = (file.field_name, (file.name, content, 'application/octet-stream'))
            ret_files += [f]

        for key, value in self.params.items():
            ret_data[key] = value

        return ret_files, ret_data, need_close

    def delete_tmp_files(self):
        for file in self.files:
            file.delete()

    def add_param(self, field_name, val):  # type: (str, str) -> None
        self.params[field_name] = val

    def add_file(self, field_name, file):
        # type: (str, FormDataFile) -> None
        file.field_name = field_name
        self.files += [file]
