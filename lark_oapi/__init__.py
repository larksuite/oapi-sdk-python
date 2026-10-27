from . import api as _api
from .card import *
from .client import Client
from .core import *
from .event.context import EventContext
from .event.custom import CustomizedEvent
from .scene.registration import register_app, aregister_app

_LAZY_ROOT_EXPORTS = {
    "ws": (".ws", None),
    "EventDispatcherHandler": (".event.dispatcher_handler", "EventDispatcherHandler"),
    "WebhookCredentials": (".event.dispatcher_handler", "WebhookCredentials"),
    "WebhookCredentialsProvider": (".event.dispatcher_handler", "WebhookCredentialsProvider"),
}


def __getattr__(name):
    if name in _LAZY_ROOT_EXPORTS:
        from importlib import import_module

        module_name, export_name = _LAZY_ROOT_EXPORTS[name]
        module = import_module(module_name, __name__)
        value = module if export_name is None else getattr(module, export_name)
    elif name in _api.__all__:
        value = getattr(_api, name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_api.__all__) | set(_LAZY_ROOT_EXPORTS))


__all__ = (
    [name for name in globals() if not name.startswith("_")]
    + _api.__all__
    + list(_LAZY_ROOT_EXPORTS)
)

# ``lark_oapi.channel`` is available as a submodule but NOT eagerly imported
# — most users of this SDK don't need the high-level Feishu Channel layer,
# and eagerly importing it would pull dozens of additional submodules and
# add measurable import latency for everyone. Users who want the Channel
# layer should import it explicitly::
#
#     from lark_oapi.channel import FeishuChannel
