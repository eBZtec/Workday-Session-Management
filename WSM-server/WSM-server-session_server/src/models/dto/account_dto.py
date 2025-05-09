from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from src.enums.types import JourneyType
from src.models.schema.request_models import SessionTerminationActionSchema


@dataclass
class AccountDTO:
    uid: str
    start_time: str
    end_time: str
    uf: str
    st: str
    c: int
    weekdays: str
    cn: str
    l: str
    enable: bool  = True
    lock: bool  = False
    unrestricted: bool = False
    journey: JourneyType = JourneyType.FIXED_TIME
    active_directory_account_status: Union[bool, None] = None
    block_station_during_interval: Union[bool, None] = False
    deactivation_date: Union[datetime, None] = None
    allowed_work_hours: Union[str, None] = None
    session_termination_action: SessionTerminationActionSchema = SessionTerminationActionSchema.LOGOFF
    work_time: Union[datetime, None] = None
    block_station_during_interval_in_minutes: Union[int, None] = None
    disable_reason: Union[str, None] = None
    formatted_work_hours: Union[str, None] = None

"""
    def __post_init__(self):
        self.uid = self.uid.lower() if self.uid else self.uid

"""