from src.logs.logger import logger
from src.config import config
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from sqlalchemy import and_
from datetime import datetime

class WorkingHoursService:
    
    def __init__(self):
        self.dm = DatabaseManager()

    def get_allowed_schedule(self, uid):
        try:
            schedule = self.dm.get_user_schedule(uid)
        except Exception as e:
            return None
        return schedule
