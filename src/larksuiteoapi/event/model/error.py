# -*- coding: UTF-8 -*-

class HandlerNotFoundError(RuntimeError):
    def __init__(self, *args):  # type: (object) -> None
        super(HandlerNotFoundError, self).__init__(args)
