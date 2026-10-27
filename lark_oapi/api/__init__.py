"""Lazy access to generated Lark API product groups.

Importing one product group should not load every generated API version and model.
"""

from importlib import import_module
from pkgutil import iter_modules


__all__ = sorted(
    module.name
    for module in iter_modules(__path__)
    if module.ispkg and module.name != "gray_test_open_sg"
)


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f".{name}", __name__)
    globals()[name] = module
    return module


def __dir__():
    return sorted(set(globals()) | set(__all__))
