from enum import Enum, IntEnum


class JourneyType(str, Enum):
    FIXED_TIME = "FIXED_TIME"
    FREE_TIME = "FREE_TIME"
    FLEX_TIME = "FLEX_TIME"


class WorkTimeType(str, Enum):
    IN = "IN"
    OUT = "OUT"


class WorkDayType(str, Enum):
    NIGHT_SHIFT = "NIGHT_SHIFT"
    DAY_SHIFT = "DAY_SHIFT"


class WeekDay(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WorkDay(IntEnum):
    WORK = 1
    NOT_WORK = 0