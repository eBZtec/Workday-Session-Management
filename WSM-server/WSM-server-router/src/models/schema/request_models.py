from pydantic import BaseModel
from typing import Optional
from datetime import datetime
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
    employee_id: str
    start_time: datetime
    end_time: datetime
    allowed_work: AllowedWorkSchema
    uf:str
    st: str
    c: str
    weekdays: str
    session_termination_action: SessionTerminationActionSchema
    cn: str
    l: str
    unrestricted: bool
    lock: bool = False
    enable: bool = True
    deactivation_date: Optional[datetime] = None
    block_station_during_interval: bool = False
    block_station_during_interval_in_minutes: int | None = 0


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
    c : str
    week_days_count: str
    extension_active: int
    ou: int

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

