# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class Machine(object):
    _types = {
        "machine_sn": str,
        "machine_name": str,
    }

    def __init__(self, d=None):
        self.machine_sn: Optional[str] = None
        self.machine_name: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MachineBuilder":
        return MachineBuilder()


class MachineBuilder(object):
    def __init__(self) -> None:
        self._machine = Machine()

    def machine_sn(self, machine_sn: str) -> "MachineBuilder":
        self._machine.machine_sn = machine_sn
        return self

    def machine_name(self, machine_name: str) -> "MachineBuilder":
        self._machine.machine_name = machine_name
        return self

    def build(self) -> "Machine":
        return self._machine