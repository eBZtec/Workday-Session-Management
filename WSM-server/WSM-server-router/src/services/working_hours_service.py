from src.logs.logger import Logger
from src.config import config
from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours
from sqlalchemy import and_
from datetime import datetime

class WorkingHoursService:
    
    def __init__(self):
        self.logger = Logger(log_name=self.__class__.__name__).get_logger()
        self.dm = DatabaseManager()



    def get_allowed_schedule(self, uid):
        try:
            schedule = self.dm.get_user_schedule(uid)
        except Exception as e:
            return None
        return schedule


    #check if the client session starts between start and end standart working hours
    def check_valid_session(self, uid):

        
        return