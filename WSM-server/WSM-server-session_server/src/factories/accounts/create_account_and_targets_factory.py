from src.interfaces.icreate_account_and_targets import ICreateAccountAndTargets
from src.models.schema.request_models import StandardWorkHoursSchema


class CreateAccountAndTargetsFactory:
    @staticmethod
    def create(standard_work_hours: StandardWorkHoursSchema) -> ICreateAccountAndTargets:
        pass