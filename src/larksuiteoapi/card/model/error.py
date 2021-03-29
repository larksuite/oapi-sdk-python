# -*- coding: UTF-8 -*-

class HandlerNotFoundError(RuntimeError):
    def __init__(self, *args):  # type: (object) -> None
        super(HandlerNotFoundError, self).__init__(args)


class SignatureError(RuntimeError):
    def __init__(self, *args):  # type: (object) -> None
        super(SignatureError, self).__init__(args)


class TokenInvalidError(RuntimeError):
    def __init__(self, *args):  # type: (object) -> None
        super(TokenInvalidError, self).__init__(args)
