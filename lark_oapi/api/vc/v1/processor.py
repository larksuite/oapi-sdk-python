# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type

from lark_oapi.event.processor import IEventProcessor
from .model.p2_vc_meeting_all_meeting_ended_v1 import P2VcMeetingAllMeetingEndedV1
from .model.p2_vc_meeting_all_meeting_started_v1 import P2VcMeetingAllMeetingStartedV1
from .model.p2_vc_meeting_join_meeting_v1 import P2VcMeetingJoinMeetingV1
from .model.p2_vc_meeting_leave_meeting_v1 import P2VcMeetingLeaveMeetingV1
from .model.p2_vc_meeting_meeting_ended_v1 import P2VcMeetingMeetingEndedV1
from .model.p2_vc_meeting_meeting_started_v1 import P2VcMeetingMeetingStartedV1
from .model.p2_vc_meeting_recording_ended_v1 import P2VcMeetingRecordingEndedV1
from .model.p2_vc_meeting_recording_ready_v1 import P2VcMeetingRecordingReadyV1
from .model.p2_vc_meeting_recording_started_v1 import P2VcMeetingRecordingStartedV1
from .model.p2_vc_meeting_share_ended_v1 import P2VcMeetingShareEndedV1
from .model.p2_vc_meeting_share_started_v1 import P2VcMeetingShareStartedV1
from .model.p2_vc_reserve_config_updated_v1 import P2VcReserveConfigUpdatedV1
from .model.p2_vc_room_created_v1 import P2VcRoomCreatedV1
from .model.p2_vc_room_deleted_v1 import P2VcRoomDeletedV1
from .model.p2_vc_room_updated_v1 import P2VcRoomUpdatedV1
from .model.p2_vc_room_level_created_v1 import P2VcRoomLevelCreatedV1
from .model.p2_vc_room_level_deleted_v1 import P2VcRoomLevelDeletedV1
from .model.p2_vc_room_level_updated_v1 import P2VcRoomLevelUpdatedV1


class P2VcMeetingAllMeetingEndedV1Processor(IEventProcessor[P2VcMeetingAllMeetingEndedV1]):
    def __init__(self, f: Callable[[P2VcMeetingAllMeetingEndedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingAllMeetingEndedV1]:
        return P2VcMeetingAllMeetingEndedV1

    def do(self, data: P2VcMeetingAllMeetingEndedV1) -> None:
        self.f(data)


class P2VcMeetingAllMeetingStartedV1Processor(IEventProcessor[P2VcMeetingAllMeetingStartedV1]):
    def __init__(self, f: Callable[[P2VcMeetingAllMeetingStartedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingAllMeetingStartedV1]:
        return P2VcMeetingAllMeetingStartedV1

    def do(self, data: P2VcMeetingAllMeetingStartedV1) -> None:
        self.f(data)


class P2VcMeetingJoinMeetingV1Processor(IEventProcessor[P2VcMeetingJoinMeetingV1]):
    def __init__(self, f: Callable[[P2VcMeetingJoinMeetingV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingJoinMeetingV1]:
        return P2VcMeetingJoinMeetingV1

    def do(self, data: P2VcMeetingJoinMeetingV1) -> None:
        self.f(data)


class P2VcMeetingLeaveMeetingV1Processor(IEventProcessor[P2VcMeetingLeaveMeetingV1]):
    def __init__(self, f: Callable[[P2VcMeetingLeaveMeetingV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingLeaveMeetingV1]:
        return P2VcMeetingLeaveMeetingV1

    def do(self, data: P2VcMeetingLeaveMeetingV1) -> None:
        self.f(data)


class P2VcMeetingMeetingEndedV1Processor(IEventProcessor[P2VcMeetingMeetingEndedV1]):
    def __init__(self, f: Callable[[P2VcMeetingMeetingEndedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingMeetingEndedV1]:
        return P2VcMeetingMeetingEndedV1

    def do(self, data: P2VcMeetingMeetingEndedV1) -> None:
        self.f(data)


class P2VcMeetingMeetingStartedV1Processor(IEventProcessor[P2VcMeetingMeetingStartedV1]):
    def __init__(self, f: Callable[[P2VcMeetingMeetingStartedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingMeetingStartedV1]:
        return P2VcMeetingMeetingStartedV1

    def do(self, data: P2VcMeetingMeetingStartedV1) -> None:
        self.f(data)


class P2VcMeetingRecordingEndedV1Processor(IEventProcessor[P2VcMeetingRecordingEndedV1]):
    def __init__(self, f: Callable[[P2VcMeetingRecordingEndedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingRecordingEndedV1]:
        return P2VcMeetingRecordingEndedV1

    def do(self, data: P2VcMeetingRecordingEndedV1) -> None:
        self.f(data)


class P2VcMeetingRecordingReadyV1Processor(IEventProcessor[P2VcMeetingRecordingReadyV1]):
    def __init__(self, f: Callable[[P2VcMeetingRecordingReadyV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingRecordingReadyV1]:
        return P2VcMeetingRecordingReadyV1

    def do(self, data: P2VcMeetingRecordingReadyV1) -> None:
        self.f(data)


class P2VcMeetingRecordingStartedV1Processor(IEventProcessor[P2VcMeetingRecordingStartedV1]):
    def __init__(self, f: Callable[[P2VcMeetingRecordingStartedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingRecordingStartedV1]:
        return P2VcMeetingRecordingStartedV1

    def do(self, data: P2VcMeetingRecordingStartedV1) -> None:
        self.f(data)


class P2VcMeetingShareEndedV1Processor(IEventProcessor[P2VcMeetingShareEndedV1]):
    def __init__(self, f: Callable[[P2VcMeetingShareEndedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingShareEndedV1]:
        return P2VcMeetingShareEndedV1

    def do(self, data: P2VcMeetingShareEndedV1) -> None:
        self.f(data)


class P2VcMeetingShareStartedV1Processor(IEventProcessor[P2VcMeetingShareStartedV1]):
    def __init__(self, f: Callable[[P2VcMeetingShareStartedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcMeetingShareStartedV1]:
        return P2VcMeetingShareStartedV1

    def do(self, data: P2VcMeetingShareStartedV1) -> None:
        self.f(data)


class P2VcReserveConfigUpdatedV1Processor(IEventProcessor[P2VcReserveConfigUpdatedV1]):
    def __init__(self, f: Callable[[P2VcReserveConfigUpdatedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcReserveConfigUpdatedV1]:
        return P2VcReserveConfigUpdatedV1

    def do(self, data: P2VcReserveConfigUpdatedV1) -> None:
        self.f(data)


class P2VcRoomCreatedV1Processor(IEventProcessor[P2VcRoomCreatedV1]):
    def __init__(self, f: Callable[[P2VcRoomCreatedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomCreatedV1]:
        return P2VcRoomCreatedV1

    def do(self, data: P2VcRoomCreatedV1) -> None:
        self.f(data)


class P2VcRoomDeletedV1Processor(IEventProcessor[P2VcRoomDeletedV1]):
    def __init__(self, f: Callable[[P2VcRoomDeletedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomDeletedV1]:
        return P2VcRoomDeletedV1

    def do(self, data: P2VcRoomDeletedV1) -> None:
        self.f(data)


class P2VcRoomUpdatedV1Processor(IEventProcessor[P2VcRoomUpdatedV1]):
    def __init__(self, f: Callable[[P2VcRoomUpdatedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomUpdatedV1]:
        return P2VcRoomUpdatedV1

    def do(self, data: P2VcRoomUpdatedV1) -> None:
        self.f(data)


class P2VcRoomLevelCreatedV1Processor(IEventProcessor[P2VcRoomLevelCreatedV1]):
    def __init__(self, f: Callable[[P2VcRoomLevelCreatedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomLevelCreatedV1]:
        return P2VcRoomLevelCreatedV1

    def do(self, data: P2VcRoomLevelCreatedV1) -> None:
        self.f(data)


class P2VcRoomLevelDeletedV1Processor(IEventProcessor[P2VcRoomLevelDeletedV1]):
    def __init__(self, f: Callable[[P2VcRoomLevelDeletedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomLevelDeletedV1]:
        return P2VcRoomLevelDeletedV1

    def do(self, data: P2VcRoomLevelDeletedV1) -> None:
        self.f(data)


class P2VcRoomLevelUpdatedV1Processor(IEventProcessor[P2VcRoomLevelUpdatedV1]):
    def __init__(self, f: Callable[[P2VcRoomLevelUpdatedV1], None]):
        self.f = f

    def type(self) -> Type[P2VcRoomLevelUpdatedV1]:
        return P2VcRoomLevelUpdatedV1

    def do(self, data: P2VcRoomLevelUpdatedV1) -> None:
        self.f(data)
