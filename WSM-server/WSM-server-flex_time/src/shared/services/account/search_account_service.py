from sqlalchemy.orm import Session

from src.config.wsm_logger import WSMLogger as wsm_logger
from src.shared.models.db.models import StandardWorkHours, FlexTime
from src.shared.repository.wsm_repository import WSMRepository


class SearchAccountService(WSMRepository):

    def __init__(self, session: Session):
        self.session = session

    def get_account_by_uid(self, uid: str) -> list[StandardWorkHours]:
        wsm_logger.debug(f"Starting process to search account by uid {uid}")
        _filter = {"uid": uid}
        wsm_logger.debug(f"Searching account with filter {_filter}")
        account = self.get_by_filter(self.session, StandardWorkHours, _filter)
        wsm_logger.debug(f"Search result: {account}")

        return account

    def get_last_flex_time_by_account_id(self, _id: int) -> FlexTime:
        wsm_logger.debug(f"Starting process to search the last flex time registered by id {_id}")
        _filter = {"std_wrk_id": _id}
        wsm_logger.debug(f"Searching the last flex time with filter {_filter}")
        result = self.get_last_record(self.session, FlexTime, _filter)
        wsm_logger.debug(f"Search result: {result}")
        return result