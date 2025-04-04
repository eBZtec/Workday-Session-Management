from abc import ABC, abstractmethod

from src.models.schema.request_models import StandardWorkHoursSchema


class ICreateAccountAndTargets(ABC):
    @abstractmethod
    async def execute(cls, standard_work_hours: StandardWorkHoursSchema) -> str:
        pass