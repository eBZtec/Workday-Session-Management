from pydantic import BaseModel, Field, field_validator, AwareDatetime
from pydantic_extra_types.timezone_name import TimeZoneName
from typing import Optional, List, Dict, Union
from datetime import datetime, time
from enum import Enum

from src.enums.target_status_type import TargetStatusType
from src.enums.types import JourneyType


class AllowedWorkSchema(str, Enum):
    YES = "Y"
    NO = "N"
    
class SessionTerminationActionSchema(str, Enum):
    LOGOFF = "logoff"
    LOCK = "lock"

class DeactivationSchema(BaseModel):
    uid: str
    deactivation_time: datetime

class StandardWorkHoursSchema(BaseModel):
    uid: str
    start_time: str
    end_time: str
    allowed_work_hours: Optional[str] = None
    journey: JourneyType = JourneyType.FIXED_TIME
    uf:str
    st: str
    c: int
    weekdays: str
    session_termination_action: SessionTerminationActionSchema = SessionTerminationActionSchema.LOGOFF
    cn: str
    l: str
    enable: bool = True
    unrestricted: bool = False
    deactivation_date: Optional[datetime] = None


class FlexTimeSchema(StandardWorkHoursSchema):
    work_time: datetime


class EventsSchema(BaseModel):
    event_type: str

class ExceptionsSchema(BaseModel):
    type: str
    ip_address: str

class ExtendedWorkHoursSchema(BaseModel):
    uid : str
    extension_start_time: datetime
    extension_end_time: datetime
    extended_workhours_type: str = "ex"
    uf : str = "BR"
    c : int = 0
    week_days_count: str = ""
    extension_active: int = 0
    ou: int = 0

class ExtendedWorkHoursResponse(ExtendedWorkHoursSchema):
    id: int

class HolidaysSchema(BaseModel):
    holiday_date: str
    city:str
    holiday_type: str

class MessagesSchema(BaseModel):
    uid : str
    message : str

class SessionsSchema(BaseModel):
    status: str

class TargetStatusSchema(BaseModel):
    uuid : str

class TargetSchema(BaseModel):
    target: str
    service: str
    enabled: TargetStatusType = TargetStatusType.ENABLE

class DisconnectRequestSchema(BaseModel):
    user:str
    hostname:str
    dc_datetime: datetime

### Calcula Jornada

class TimeRange(BaseModel):
    start: time
    end: time

class AccountTargetStatusResponse(BaseModel):
    target: str = None
    update_timestamp: datetime

class StandardWorkHoursResponse(StandardWorkHoursSchema):
    id: int
    overtimes: List[ExtendedWorkHoursSchema] = None
    target_status: List[AccountTargetStatusResponse] = None
    create_timestamp: datetime
    update_timestamp: datetime

### NTP Server

class LocationRequest(BaseModel):
    country: str
    state: str
    city: str


class NTP_response(BaseModel):
    ntp : str
    local_time: str
    country: str
    state: str
    city: str


### Hostname x Sessions

class HostnameSessions(BaseModel):
    hostname: str
    user: str
    status: str
    start_time: datetime


class OnlineHostInfoResponse(BaseModel):
    hostname:str
    user:str
    client_ip_address: str
    client_cli_version: str
    client_os_name: str
    client_os_version: str
    client_uptime: str
    client_agent_info: str

