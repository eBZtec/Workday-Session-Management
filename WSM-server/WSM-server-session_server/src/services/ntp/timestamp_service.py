from src.connections.database_manager import DatabaseManager
from src.models.models import Sessions
from src.config.wsm_logger import logger
from src.config import config


class TimestampService():

    async def user_timestamp(uid:str) -> Sessions :

        try:
            databaseManager = DatabaseManager()
            return databaseManager.get_user_session_timezone(uid)
        except KeyError:
            logger.error(f"UID {uid} not found in the database.")
            return None  # Ou lançar uma exceção específica
        except ConnectionError:
            logger.error("Database connection error while fetching session.")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in get_timestamp_execute: {str(e)}")
            return None
