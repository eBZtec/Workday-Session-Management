from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime, time
from enum import Enum

class AllowedWorkSchema(str, Enum):
    YES = "Y"
    NO = "N"
    
class SessionTerminationActionSchema(str, Enum):
    LOGOFF = "logoff"
    LOCK = "lock"