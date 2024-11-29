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