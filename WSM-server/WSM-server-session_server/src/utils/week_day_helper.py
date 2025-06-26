from datetime import date
from enum import IntEnum


class WeekDay(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WorkDay(IntEnum):
    WORK = 1
    NOT_WORK = 0


def update_work_week_days(normal_week_days: str, holidays: list[date]) -> list[int]:
    work_week_days = []

    for i in normal_week_days:
        work_week_days.append(int(i))

    for i, holiday in enumerate(holidays):
        holiday_week_day = holiday.weekday()

        if holiday_week_day == WeekDay.SUNDAY:
            work_week_days[0] = WorkDay.NOT_WORK
        else:
            work_week_days[i + 1] = WorkDay.NOT_WORK

    return work_week_days


def is_able_to_work(data: date, work_days: str) -> bool:
    if len(work_days) != 7 or not all(c in '01' for c in work_days):
        raise ValueError("Dias das semana de trabalho deve conter 7 caracteres com '0' ou '1' (domingo a sábado)")

    week_day = data.weekday()  # 0 = segunda, ..., 6 = domingo
    idx = (week_day + 1) % 7  # converte para 0=domingo, ..., 6=sábado

    return work_days[idx] == '1'