from pydantic import BaseModel, Field, field_validator, AwareDatetime
from typing import Optional, List, Dict, Union
from datetime import datetime, time
from enum import Enum

from src.enums.target_status_type import TargetStatusType


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




