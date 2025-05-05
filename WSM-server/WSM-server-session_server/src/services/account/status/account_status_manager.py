from src.connections.database_manager import DatabaseManager
from src.models.models import StandardWorkHours


class AccountStatusManager:

    @staticmethod
    async def enable(uid: str):
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = {"enable": True, "disable_reason": None}
            database_manager.update_entry(StandardWorkHours, account.id, entry)

            account.enable = True

            return account
        else:
            raise Exception(f"Account not find or uid \"{uid}\"")

    @staticmethod
    async def disable(uid: str, disable_reason: str):
        database_manager = DatabaseManager()

        account: StandardWorkHours | None = database_manager.get_by_uid(StandardWorkHours, uid)

        if account:
            entry = {"enable": False, "disable_reason": disable_reason}
            database_manager.update_entry(StandardWorkHours, account.id, entry)

            account.enable = False
        else:
            raise Exception(f"Account not find or uid \"{uid}\"")