class NoAuthorizationException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg


class ClientAssertionException(Exception):
    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"{self.code}: {self.msg}"


class AccessTokenException(Exception):
    def __init__(self, status_code: int, code: int, error: str, error_description: str):
        super().__init__(error_description or error or "access token request failed")
        self.status_code = status_code
        self.code = code
        self.error = error
        self.error_description = error_description

    def __str__(self):
        msg = self.error_description or self.error or "access token request failed"
        return f"statusCode:{self.status_code}, code:{self.code}, msg:{msg}"


class ObtainAccessTokenException(Exception):
    def __init__(self, desc: str, code: int, msg: str):
        self.desc = desc
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"{self.desc}, code: {self.code}, msg: {self.msg}"


class UnmarshalException(Exception):
    def __init__(self, dst, src, field):
        self.dst = dst
        self.src = src
        self.field = field

    def __str__(self):
        return f"expected {self.dst} but was {self.src} at field: {self.field}"


class InvalidArgsException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg


class AccessDeniedException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg


class EventException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg


class CardException(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg
