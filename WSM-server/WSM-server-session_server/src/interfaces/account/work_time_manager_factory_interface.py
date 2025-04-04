from abc import abstractmethod, ABC

from src.models.schema.request_models import StandardWorkHoursSchema


class WorkTimeManagerFactoryInterface(ABC):
    @abstractmethod
    async def execute(cls, standard_work_hours: StandardWorkHoursSchema) -> str:
        pass