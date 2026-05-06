import base64
import hashlib
from typing import Union

from Crypto.Cipher import AES

from ..const import UTF_8


class AESCipher(object):
    def __init__(self, key: Union[str, bytes]) -> None:
        if isinstance(key, str):
            key = key.encode(UTF_8)
        self.digest = hashlib.sha256(key).digest()

    def decrypt(self, enc: bytes) -> bytes:
        if len(enc) < AES.block_size * 2 or len(enc) % AES.block_size != 0:
            raise ValueError("invalid ciphertext length")
        iv = enc[: AES.block_size]
        cipher = AES.new(self.digest, AES.MODE_CBC, iv)
        s = cipher.decrypt(enc[AES.block_size:])
        if not s:
            raise ValueError("invalid ciphertext: empty plaintext")
        pad = s[-1]
        if pad < 1 or pad > AES.block_size or pad > len(s):
            raise ValueError("invalid PKCS7 padding")
        if s[-pad:] != bytes([pad]) * pad:
            raise ValueError("invalid PKCS7 padding")
        return s[:-pad]

    def decrypt_str(self, enc: str) -> str:
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode(UTF_8)
