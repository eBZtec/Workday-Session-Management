from pydantic import BaseModel, Field, field_validator, AwareDatetime
from typing import Optional, List, Dict
from datetime import datetime, time
from enum import Enum

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
    # employee_id: str
    start_time: str
    end_time: str
    allowed_work_hours: Optional[str] = None
    uf:str
    st: str
    c: int
    weekdays: str
    session_termination_action: SessionTerminationActionSchema
    cn: str
    l: str
    enable: bool = True
    unrestricted: bool = False
    deactivation_date: Optional[datetime] = None


class StandardWorkHoursResponse(StandardWorkHoursSchema):
    id: int
    create_timestamp: datetime
    update_timestamp: datetime

class EventsSchema(BaseModel):
    event_type: str

class ExceptionsSchema(BaseModel):
    type: str
    ip_address: str

class ExtendedWorkHoursSchema(BaseModel):
    uid : str
    extension_start_time: datetime
    extension_end_time: datetime
    extended_workhours_type: str
    uf : str
    c : int
    week_days_count: str
    extension_active: int
    ou: int

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
    enabled: int

class DisconnectRequestSchema(BaseModel):
    user:str
    hostname:str
    dc_datetime: datetime

### Calcula Jornada

class TimeRange(BaseModel):
    start: time
    end: time


