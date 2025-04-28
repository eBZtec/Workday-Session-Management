from src.connections.database_manager import DatabaseManager
from src.models.models import Configuration
from src.models.schema.request_models import ConfigurationRequest


class ConfigurationManagerService:
    @staticmethod
    async def update(config: ConfigurationRequest):
        database_manager = DatabaseManager()

        entry = config.model_dump()
        database_manager.update_entry(Configuration, 1, entry)