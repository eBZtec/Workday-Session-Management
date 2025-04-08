from enum import Enum


class AllowedWorkSchema(str, Enum):
    YES = "Y"
    NO = "N"


class SessionTerminationActionSchema(str, Enum):
    LOGOFF = "logoff"
    LOCK = "lock"