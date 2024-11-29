from enum import Enum

class LogonEventType(Enum):
    LOGON_SUCCESS = "4624"   # A user successfully logged on to a computer
    LOGON_FAILURE = "4625"   # Logon failure with an unknown user or bad password
    LOGOFF_COMPLETE = "4634" # The logoff process was completed for a user
    LOGOFF_INITIATED = "4647" # A user initiated the logoff process
    LOGON_WITH_CREDENTIALS = "4648" # Logged on using explicit credentials as another user
    DISCONNECT_SESSION = "4779" # A user disconnected a terminal server session
    LOCK_SESSION = "4800" # Session was locked
    UNLOCK_SESSION = "4801" # Session unlocked