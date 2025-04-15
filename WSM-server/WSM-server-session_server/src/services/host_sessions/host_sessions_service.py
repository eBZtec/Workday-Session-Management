from src.connections.database_manager import DatabaseManager
from src.config.wsm_logger import logger
from src.config import config
from src.models.models import Sessions


class hostSessionService:

    async def get_all_hosts_sessions() -> Sessions:
        try:
            databaseManager = DatabaseManager()
            all_hosts = databaseManager.get_all_hosts_sessions()
            return all_hosts
        except KeyError:
            logger.error(f"Sessions not found in the database.")
            return None  # Ou lançar uma exceção específica
        except ConnectionError:
            logger.error("Database connection error while fetching session.")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_host_sessions_execute: {str(e)}")
            return None
        
    async def get_host_session(hostname : str)-> Sessions:
        try:
            databaseManager = DatabaseManager()
            return databaseManager.get_host_sessions(hostname)
        except KeyError:
            logger.error(f"Sessions not found in for hostname: {hostname}.")
            return None  # Ou lançar uma exceção específica
        except ConnectionError:
            logger.error("Database connection error while fetching session.")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_host_sessions_execute: {str(e)}")
            return None