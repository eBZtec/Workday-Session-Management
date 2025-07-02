from fastapi import HTTPException,status

from src.config.wsm_logger import logger
from src.models.schema.request_models import ExtendedWorkHoursSchema
from src.services.account.presenter.search_account_by_uid_service import SearchAccountByUIDService
from src.services.overtime.insert_overtime_database_service import InsertOvertimeDatabaseService
from src.services.pooling.accounts_pooling_service import AccountsPoolingService


class InsertOvertimeController:

    @staticmethod
    async def execute(overtime_data: ExtendedWorkHoursSchema):
        try:
            account = await SearchAccountByUIDService.execute(overtime_data.uid)
            if account:
                await InsertOvertimeDatabaseService.execute(overtime_data, account.id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Account \"{overtime_data.uid}\" not found"
                )
        except HTTPException as e:
            raise e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Could not insert overtime {overtime_data.model_dump()}, reason: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        else:
            logger.info(f"Overtime {overtime_data.model_dump()} inserted successfully into the database")
            try:
                logger.info(f"Starting process account pooling to update account {account.uid}")
                await AccountsPoolingService.execute(account.uid)
            except Exception as e:
                logger.error(f"Could not send message for data {overtime_data.model_dump()}, reason: {e}")

