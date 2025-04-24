from datetime import datetime

from src.config.wsm_logger import logger
from src.connections.database_manager import DatabaseManager
from src.models.models import FlexTime, StandardWorkHours


class SearchFlexTimePresenter:
    @staticmethod
    def get_flex_time_by_user_and_date(uid: str, date_from: datetime = None, date_to: datetime = None, skip = 0, limit = 10) -> list[FlexTime] | None:
        result = []
        try:
            logger.info(f"Starting process to get all flex times by user {uid}")
            logger.debug(f"Searching by user id {uid}, date from {date_from}, date to {date_to}, skip {skip}, limit {limit}")

            database_manager = DatabaseManager()

            account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

            if account:
                logger.info(f"Found account id {account.id} for user {uid}")
                result = database_manager.get_flex_time_by_user_and_date_with_pagination(
                    account.id,
                    date_from,
                    date_to,
                    skip,
                    limit
                )
                logger.info(f"Found {len(result)} flex times register for user {uid}")
            else:
                logger.warn(f"Account not found for user {uid}")
        except Exception as e:
            logger.error(f"Failed to search account, reason {e}")
        finally:
            return result