# -*- coding: UTF-8 -*-
# This file is originally modified from https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM

import base64
import hashlib
import json

from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key):  # type: (bytes) -> None
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):  # type: (bytes) -> bytes
        u_type = type(b"".decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    @staticmethod
    def _unpad(s):  # type: (bytes) -> bytes
        return s[:-ord(s[len(s) - 1:])]

    def decrypt(self, enc):  # type: (bytes) -> bytes
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def decrypt_string(self, enc):  # type: (bytes) -> str
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode('utf8')


# encrypt = "P37w+VZImNgPEO1RBhJ6RtKl7n6zymIbEG1pReEzghk="
# cipher = AESCipher("test key")
# print("Decrypted string:\n{}".format(cipher.decrypt_string(encrypt)))

def decrypt(encrypt, key):  # type: (bytes, bytes) -> str
    json_obj = json.loads(encrypt)
    cipher = AESCipher(key)
    return cipher.decrypt_string(json_obj['encrypt'])
