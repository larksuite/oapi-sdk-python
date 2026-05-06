from . import ws
from .api import *
from .card import *
from .client import Client
from .core import *
from .event.context import EventContext
from .event.custom import CustomizedEvent
from .event.dispatcher_handler import EventDispatcherHandler
from .scene.registration import register_app, aregister_app

# ``lark_oapi.channel`` is available as a submodule but NOT eagerly imported
# — most users of this SDK don't need the high-level Feishu Channel layer,
# and eagerly importing it would pull dozens of additional submodules and
# add measurable import latency for everyone. Users who want the Channel
# layer should import it explicitly::
#
#     from lark_oapi.channel import FeishuChannel
