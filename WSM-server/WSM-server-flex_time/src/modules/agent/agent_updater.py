import json

import zmq

from src.config.wsm_config import wsm_config
from src.config.wsm_logger import wsm_logger
from src.infra.wsm_session_database import wsm_session_database
from src.infra.wsm_zeromq_manager import wsm_zeromq_manager
from src.shared.enums.types import JourneyType
from src.shared.services.account.search_account_service import SearchAccountService
from src.shared.services.flextime.calculate_flextime_service import CalculateFlextimeService


class AgentUpdaterServer:
    @staticmethod
    def start():

        while True:
            try:
                wsm_logger.info(f"Waiting message on ZeroMQ \"{wsm_config.wsm_zeromq_url}\" host...")
                uid = wsm_zeromq_manager.get_socket().recv_string()
                wsm_logger.info(f"Received ZeroMQ message \"{uid}\"")
            except zmq.ZMQError as e:
                wsm_logger.error(f"WSM - simple_route_server_service - ZQM error: {e}")
            except Exception as e:
                wsm_logger.error(f"WSM - simple_route_server_service - ZQM error: {e}")
            else:
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

                            wsm_logger.info(f"Account update response for agent {response}")

                            wsm_zeromq_manager.get_socket().send_string(response)
                            wsm_logger.info("Message sent successfully for ZeroMQ host")
                        else:
                            wsm_logger.warning(f"Skipping processing, reason: Journey defined as {account.journey} for uid {account.uid}")
                    elif len(accounts) > 1:
                        wsm_logger.warning(f"Found more the one account for uid {uid}")
                    else:
                        wsm_logger.warning(f"No account was found for uid {uid}")