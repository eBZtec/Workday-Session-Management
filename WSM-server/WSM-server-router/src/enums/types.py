from enum import Enum

class JourneyType(str, Enum):
    FIXED_TIME = "FIXED_TIME"
    FREE_TIME = "FREE_TIME"
    FLEX_TIME = "FLEX_TIME"


class WorkTimeType(str, Enum):
    IN = "IN"
    OUT = "OUT"
