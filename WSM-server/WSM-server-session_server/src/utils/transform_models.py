from src.models.dto.account_dto import AccountDTO
from src.models.schema.request_models import StandardWorkHoursSchema, FlexTimeSchema


def account_dto_to_standard_work_hours_schema(account_dto: AccountDTO) -> StandardWorkHoursSchema:
    standard_work_hours = StandardWorkHoursSchema(
        uid=account_dto.uid,
        start_time=account_dto.start_time,
        end_time=account_dto.end_time,
        allowed_work_hours=account_dto.allowed_work_hours,
        journey=account_dto.journey,
        uf=account_dto.uf,
        st=account_dto.st,
        c=account_dto.c,
        weekdays=account_dto.weekdays,
        session_termination_action=account_dto.session_termination_action,
        cn=account_dto.cn,
        l=account_dto.l,
        enable=account_dto.enable,
        unrestricted=account_dto.unrestricted,
        deactivation_date=account_dto.deactivation_date
    )

    return standard_work_hours


def account_dto_to_flex_time_schema(account_dto: AccountDTO) -> StandardWorkHoursSchema:
    standard_work_hours = FlexTimeSchema(
        uid=account_dto.uid,
        start_time=account_dto.start_time,
        end_time=account_dto.end_time,
        allowed_work_hours=account_dto.allowed_work_hours,
        journey=account_dto.journey,
        uf=account_dto.uf,
        st=account_dto.st,
        c=account_dto.c,
        weekdays=account_dto.weekdays,
        session_termination_action=account_dto.session_termination_action,
        cn=account_dto.cn,
        l=account_dto.l,
        enable=account_dto.enable,
        unrestricted=account_dto.unrestricted,
        deactivation_date=account_dto.deactivation_date,
        work_time=account_dto.work_time
    )

    return standard_work_hours


def flex_time_schema_standard_work_hours(standard: StandardWorkHoursSchema) -> StandardWorkHoursSchema:
    standard_work_hours = StandardWorkHoursSchema(
        uid=standard.uid,
        start_time=standard.start_time,
        end_time=standard.end_time,
        allowed_work_hours=standard.allowed_work_hours,
        journey=standard.journey,
        uf=standard.uf,
        st=standard.st,
        c=standard.c,
        weekdays=standard.weekdays,
        session_termination_action=standard.session_termination_action,
        cn=standard.cn,
        l=standard.l,
        enable=standard.enable,
        unrestricted=standard.unrestricted,
        deactivation_date=standard.deactivation_date
    )

    return standard_work_hours