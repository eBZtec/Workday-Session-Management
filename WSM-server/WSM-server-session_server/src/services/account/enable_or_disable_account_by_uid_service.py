from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class EnableOrDisableAccountByUidService:

    @staticmethod
    async def execute(uid: str, status: bool) -> StandardWorkHours:
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = {"enable": status}
            database_manager.update_entry(StandardWorkHours, account.id, entry)

            account.enable = status

            return account
        else:
            raise Exception(f"Account not find or uid \"{uid}\"")