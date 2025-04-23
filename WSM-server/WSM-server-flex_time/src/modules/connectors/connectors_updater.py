import json

from src.config.wsm_config import wsm_config
from src.config.wsm_logger import wsm_logger
from src.infra.wsm_queue_manager import wsm_queue_manager
from src.infra.wsm_session_database import wsm_session_database
from src.shared.enums.types import JourneyType
from src.shared.services.account.search_account_service import SearchAccountService
from src.shared.services.flextime.calculate_flextime_service import CalculateFlextimeService


class ConnectorsUpdater:
    @staticmethod
    def message_callback(ch, method, properties, body):
        uid = body.decode("utf-8")
        uid = uid.strip("\"")
        wsm_logger.info(f"Message \"{uid}\" received on queue {wsm_config.wsm_queue_updater}")
        with wsm_session_database.session_scope() as session:
            search_account_service = SearchAccountService(session)

            accounts = search_account_service.get_account_by_uid(uid)

            if len(accounts) == 1:
                account = accounts[0]
                wsm_logger.info(f"Found one account for uid \"{account.uid}\"")

                if account.journey == JourneyType.FLEX_TIME:
                    calculate_work_hours_service = CalculateFlextimeService(account, session)
                    processed_account = calculate_work_hours_service.calculate()

                    data = {k: v for k, v in processed_account.__dict__.items() if not k.startswith('_')}
                    response = json.dumps(data, default=str)

                    wsm_queue_manager.send_message(response, wsm_config.wsm_queue_pooling)
                    wsm_logger.info(f"Message \"{response}\" sent on queue \"{wsm_config.wsm_queue_pooling}\"")
                else:
                    wsm_logger.warning(
                        f"Skipping processing, reason: Journey defined as {account.journey} for uid {account.uid}")
            elif len(accounts) > 1:
                wsm_logger.warning(f"Found more the one account for uid {uid}")
            else:
                wsm_logger.warning(f"No account was found for uid {uid}")

    @staticmethod
    def start():
        wsm_queue_manager.start_mq(ConnectorsUpdater.message_callback)
