# -*- coding: UTF-8 -*-
# Code generated by lark suite oapi sdk gen

from typing import List, Dict, Any
from ....utils.dt import to_json_decorator
from ....event.model.event import *
import attr




@to_json_decorator
@attr.s
class OrganizerInfo(object):
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    open_id = attr.ib(type=str, default=None, metadata={'json': 'open_id'})


@to_json_decorator
@attr.s
class RoomFreeBusy(object):
    start_time = attr.ib(type=str, default=None, metadata={'json': 'start_time'})
    end_time = attr.ib(type=str, default=None, metadata={'json': 'end_time'})
    uid = attr.ib(type=str, default=None, metadata={'json': 'uid'})
    original_time = attr.ib(type=int, default=None, metadata={'json': 'original_time'})
    organizer_info = attr.ib(type=OrganizerInfo, default=None, metadata={'json': 'organizer_info'})


@to_json_decorator
@attr.s
class Building(object):
    building_id = attr.ib(type=str, default=None, metadata={'json': 'building_id'})
    description = attr.ib(type=str, default=None, metadata={'json': 'description'})
    floors = attr.ib(type=List[str], default=None, metadata={'json': 'floors'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})


@to_json_decorator
@attr.s
class BuildingId(object):
    building_id = attr.ib(type=str, default=None, metadata={'json': 'building_id'})
    custom_building_id = attr.ib(type=str, default=None, metadata={'json': 'custom_building_id'})


@to_json_decorator
@attr.s
class Country(object):
    country_id = attr.ib(type=str, default=None, metadata={'json': 'country_id'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})


@to_json_decorator
@attr.s
class District(object):
    district_id = attr.ib(type=str, default=None, metadata={'json': 'district_id'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})


@to_json_decorator
@attr.s
class ErrorEventUid(object):
    uid = attr.ib(type=str, default=None, metadata={'json': 'uid'})
    original_time = attr.ib(type=str, default=None, metadata={'json': 'original_time'})
    error_msg = attr.ib(type=str, default=None, metadata={'json': 'error_msg'})


@to_json_decorator
@attr.s
class EventInfo(object):
    uid = attr.ib(type=str, default=None, metadata={'json': 'uid'})
    original_time = attr.ib(type=str, default=None, metadata={'json': 'original_time'})
    summary = attr.ib(type=str, default=None, metadata={'json': 'summary'})


@to_json_decorator
@attr.s
class EventUid(object):
    uid = attr.ib(type=str, default=None, metadata={'json': 'uid'})
    original_time = attr.ib(type=int, default=None, metadata={'json': 'original_time'})


@to_json_decorator
@attr.s
class Freebusy(object):
    pass


@to_json_decorator
@attr.s
class Instance(object):
    pass


@to_json_decorator
@attr.s
class Room(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    building_id = attr.ib(type=str, default=None, metadata={'json': 'building_id'})
    building_name = attr.ib(type=str, default=None, metadata={'json': 'building_name'})
    capacity = attr.ib(type=int, default=None, metadata={'json': 'capacity'})
    description = attr.ib(type=str, default=None, metadata={'json': 'description'})
    display_id = attr.ib(type=str, default=None, metadata={'json': 'display_id'})
    floor_name = attr.ib(type=str, default=None, metadata={'json': 'floor_name'})
    is_disabled = attr.ib(type=bool, default=None, metadata={'json': 'is_disabled'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})


@to_json_decorator
@attr.s
class RoomId(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    custom_room_id = attr.ib(type=str, default=None, metadata={'json': 'custom_room_id'})


@to_json_decorator
@attr.s
class Summary(object):
    pass


@to_json_decorator
@attr.s
class MeetingRoom(object):
    room_id = attr.ib(type=int, default=None, metadata={'json': 'room_id'})




@attr.s
class RoomBatchGetResult(object):
    rooms = attr.ib(type=List[Room], default=None, metadata={'json': 'rooms'})



@attr.s
class FreebusyBatchGetResult(object):
    time_min = attr.ib(type=str, default=None, metadata={'json': 'time_min'})
    time_max = attr.ib(type=str, default=None, metadata={'json': 'time_max'})
    free_busy = attr.ib(type=Dict[str, RoomFreeBusy], default=None, metadata={'json': 'free_busy'})



@attr.s
class BuildingBatchGetResult(object):
    buildings = attr.ib(type=List[Building], default=None, metadata={'json': 'buildings'})


@to_json_decorator
@attr.s
class SummaryBatchGetReqBody(object):
    event_uids = attr.ib(type=List[EventUid], default=None, metadata={'json': 'EventUids'})


@attr.s
class SummaryBatchGetResult(object):
    event_infos = attr.ib(type=List[EventInfo], default=None, metadata={'json': 'EventInfos'})
    error_event_uids = attr.ib(type=List[ErrorEventUid], default=None, metadata={'json': 'ErrorEventUids'})



@attr.s
class BuildingBatchGetIdResult(object):
    buildings = attr.ib(type=List[BuildingId], default=None, metadata={'json': 'buildings'})



@attr.s
class RoomBatchGetIdResult(object):
    rooms = attr.ib(type=List[RoomId], default=None, metadata={'json': 'rooms'})


@to_json_decorator
@attr.s
class BuildingCreateReqBody(object):
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    floors = attr.ib(type=List[str], default=None, metadata={'json': 'floors'})
    country_id = attr.ib(type=str, default=None, metadata={'json': 'country_id'})
    district_id = attr.ib(type=str, default=None, metadata={'json': 'district_id'})
    custom_building_id = attr.ib(type=str, default=None, metadata={'json': 'custom_building_id'})


@attr.s
class BuildingCreateResult(object):
    building_id = attr.ib(type=str, default=None, metadata={'json': 'building_id'})


@to_json_decorator
@attr.s
class RoomCreateReqBody(object):
    building_id = attr.ib(type=str, default=None, metadata={'json': 'building_id'})
    floor = attr.ib(type=str, default=None, metadata={'json': 'floor'})
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    capacity = attr.ib(type=int, default=None, metadata={'json': 'capacity'})
    is_disabled = attr.ib(type=bool, default=None, metadata={'json': 'is_disabled'})
    custom_room_id = attr.ib(type=str, default=None, metadata={'json': 'custom_room_id'})


@attr.s
class RoomCreateResult(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})







@attr.s
class DistrictListResult(object):
    districts = attr.ib(type=List[District], default=None, metadata={'json': 'districts'})



@attr.s
class BuildingListResult(object):
    buildings = attr.ib(type=List[Building], default=None, metadata={'json': 'buildings'})



@attr.s
class CountryListResult(object):
    countries = attr.ib(type=List[Country], default=None, metadata={'json': 'countries'})



@attr.s
class RoomListResult(object):
    rooms = attr.ib(type=List[Room], default=None, metadata={'json': 'rooms'})


@to_json_decorator
@attr.s
class InstanceReplyReqBody(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    uid = attr.ib(type=str, default=None, metadata={'json': 'uid'})
    original_time = attr.ib(type=int, default=None, metadata={'json': 'original_time'})
    status = attr.ib(type=str, default=None, metadata={'json': 'status'})



@to_json_decorator
@attr.s
class BuildingUpdateReqBody(object):
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    floors = attr.ib(type=List[str], default=None, metadata={'json': 'floors'})
    country_id = attr.ib(type=str, default=None, metadata={'json': 'country_id'})
    district_id = attr.ib(type=str, default=None, metadata={'json': 'district_id'})
    custom_building_id = attr.ib(type=str, default=None, metadata={'json': 'custom_building_id'})



@to_json_decorator
@attr.s
class RoomUpdateReqBody(object):
    name = attr.ib(type=str, default=None, metadata={'json': 'name'})
    capacity = attr.ib(type=int, default=None, metadata={'json': 'capacity'})
    is_disabled = attr.ib(type=bool, default=None, metadata={'json': 'is_disabled'})
    custom_room_id = attr.ib(type=str, default=None, metadata={'json': 'custom_room_id'})



@attr.s
class RoomCreatedEventData(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})


@attr.s
class RoomCreatedEvent(BaseEventV2):
    event = attr.ib(type=RoomCreatedEventData, default=None)



@attr.s
class RoomDeletedEventData(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})


@attr.s
class RoomDeletedEvent(BaseEventV2):
    event = attr.ib(type=RoomDeletedEventData, default=None)



@attr.s
class RoomStatusChangedEventData(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})


@attr.s
class RoomStatusChangedEvent(BaseEventV2):
    event = attr.ib(type=RoomStatusChangedEventData, default=None)



@attr.s
class RoomUpdatedEventData(object):
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})


@attr.s
class RoomUpdatedEvent(BaseEventV2):
    event = attr.ib(type=RoomUpdatedEventData, default=None)



@attr.s
class MeetingRoomStatusChangedEventData(object):
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})


@attr.s
class MeetingRoomStatusChangedEvent(BaseEventV2):
    event = attr.ib(type=MeetingRoomStatusChangedEventData, default=None)



@attr.s
class MeetingRoomCreatedEventData(object):
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})


@attr.s
class MeetingRoomCreatedEvent(BaseEventV2):
    event = attr.ib(type=MeetingRoomCreatedEventData, default=None)



@attr.s
class MeetingRoomDeletedEventData(object):
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})


@attr.s
class MeetingRoomDeletedEvent(BaseEventV2):
    event = attr.ib(type=MeetingRoomDeletedEventData, default=None)



@attr.s
class MeetingRoomUpdatedEventData(object):
    room_name = attr.ib(type=str, default=None, metadata={'json': 'room_name'})
    room_id = attr.ib(type=str, default=None, metadata={'json': 'room_id'})


@attr.s
class MeetingRoomUpdatedEvent(BaseEventV2):
    event = attr.ib(type=MeetingRoomUpdatedEventData, default=None)
