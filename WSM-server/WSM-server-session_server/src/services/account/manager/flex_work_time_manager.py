from src.models.schema.request_models import StandardWorkHoursSchema
from src.services.account.manager.work_time_manager import WorkTimeManager


class FlexWorkTimeManager(WorkTimeManager):
    async def insert(self, standard_work_hours: StandardWorkHoursSchema) -> str:
        pass

    async def update(self, standard_work_hours: StandardWorkHoursSchema):
        pass