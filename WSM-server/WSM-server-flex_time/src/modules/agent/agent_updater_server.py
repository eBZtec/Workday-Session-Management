from src.config.wsm_logger import wsm_logger
from src.infra.wsm_session_database import wsm_session_database
from src.shared.enums.types import JourneyType, WorkTimeType
from src.shared.services.account.search_account_service import SearchAccountService


class AgentUpdaterServer:
    @staticmethod
    def start():
        uid = "teste14"
        with wsm_session_database.session_scope() as session:
            search_account_service = SearchAccountService(session)

            accounts = search_account_service.get_account_by_uid(uid)

            if len(accounts) == 1:
                account = accounts[0]
                wsm_logger.info(f"Found one account for uid {account.uid}")

                if account.journey == JourneyType.FLEX_TIME:
                    wsm_logger.debug(f"Processing uid {account.uid} with journey defined as {account.journey}")
                    last_flex_time = search_account_service.get_last_flex_time_by_account_id(account.id)

                    if last_flex_time:
                        wsm_logger.info(f"Found last flex time for uid {account.uid} (work time \"{last_flex_time.work_time}\", type \"{last_flex_time.work_time_type}\")")
                        wsm_logger.debug(f"Last flex time found as {last_flex_time.as_dict()}")

                        if last_flex_time.work_time_type == WorkTimeType.OUT:
                            wsm_logger.info(f"User {account.uid} is not able to logon. Blocking user work hours....")
                        else:
                            wsm_logger.info(f"User {account.uid} is able to logon. Calculating work hours....")
                    else:
                        wsm_logger.info(f"No flex time found for uid {account.uid}, user work time must be blocked.")
                else:
                    wsm_logger.warning(f"Skipping processing, reason: Journey defined as {account.journey} for uid {account.uid}")
            elif len(accounts) > 1:
                wsm_logger.warning(f"Found more the one account for uid {uid}")
            else:
                wsm_logger.warning(f"No account was found for uid {uid}")