from typing import Optional, Dict


class RawResponse(object):

    def __init__(self):
        self.status_code: Optional[int] = None
        self.header: Dict[str, str] = {}
        self.content: Optional[bytes] = None
