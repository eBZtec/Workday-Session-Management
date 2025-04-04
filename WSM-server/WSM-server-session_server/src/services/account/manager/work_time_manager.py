from abc import ABC, abstractmethod

from src.models.schema.request_models import StandardWorkHoursSchema


class WorkTimeManager(ABC):

    @abstractmethod
    async def insert(self, standard_work_hours: StandardWorkHoursSchema) -> str:
        pass

    @abstractmethod
    async def update(self, standard_work_hours: StandardWorkHoursSchema):
        pass