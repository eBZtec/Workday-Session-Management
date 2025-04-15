import json
from datetime import time, datetime, timedelta, date
from operator import itemgetter

from pytz import timezone

from src.shared.enums.types import WorkDayType, WeekDay, WorkDay
from src.shared.models.db.models import StandardWorkHours


def today_work_time_range(account: StandardWorkHours) -> (timedelta, timedelta):
    start_work_time = string_to_time(account.start_time)
    end_work_time = string_to_time(account.end_time)

    today = datetime.today().date()
    dt1 = datetime.combine(today, start_work_time)

    if end_work_time <= start_work_time:
        today = today + timedelta(days=1)

    dt2 = datetime.combine(today, end_work_time)

    return dt1, dt2

def get_work_hours_quantity(account: StandardWorkHours) -> timedelta:
    dt1, dt2 = today_work_time_range(account)

    return dt2 - dt1


def get_work_day_type(account: StandardWorkHours) -> WorkDayType:
    start_work_time = string_to_time(account.start_time)
    end_work_time = string_to_time(account.end_time)

    if start_work_time < end_work_time:
        return WorkDayType.DAY_SHIFT
    return WorkDayType.NIGHT_SHIFT


def string_to_time(hours: str) -> time:
    return datetime.strptime(hours, "%H:%M").time()


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


def cleanup(timeframes: list[tuple[datetime, datetime]], tz = "America/Sao_Paulo"):
    result = []

    for _, timeframe in enumerate(timeframes):
        start, end = timeframe

        if start.day != end.day:
            next_day = date.fromordinal(start.toordinal() + 1)
            first_end_overtime = datetime(
                start.year,
                start.month,
                start.day,
                23,
                59,
                0,
                0,
                tzinfo=timezone(tz)
            )

            result.append((start, first_end_overtime))

            next_start_overtime = datetime(
                next_day.year,
                next_day.month,
                next_day.day,
                0,
                0,
                0,
                0,
                tzinfo=timezone("America/Sao_Paulo")
            )
            next_end_overtime = datetime(
                end.year,
                end.month,
                end.day,
                end.hour,
                end.minute,
                0,
                0,
                tzinfo=timezone("America/Sao_Paulo")
            )

            result.append((next_start_overtime, next_end_overtime))
        else:
            result.append((start, end))
    return result


def clean_work_timeframes(work_hours: list[tuple[datetime, datetime]]):
    timeframes = sorted(work_hours, key=itemgetter(0))

    x = 0
    while x < len(timeframes):
        x = x + 1
        current_timeframe = timeframes[x - 1]

        if x < len(timeframes):
            next_timeframe = timeframes[x]

            if current_timeframe[1] >= next_timeframe[0]:
                if current_timeframe[1] >= next_timeframe[1]:
                    temp_timeframe = current_timeframe
                else:
                    temp_timeframe = (current_timeframe[0], next_timeframe[1])
                timeframes.append(temp_timeframe)
                timeframes.pop(x - 1)
                timeframes.pop(x - 1)
                timeframes = sorted(timeframes, key=itemgetter(0))
                x = 0

    return timeframes


def allowed_work_days_as_json(work_hours: list[tuple[datetime, datetime]]):
    work_days = {}

    for week_day in WeekDay:
        week_day_name = week_day.name
        week_day_value = week_day.value
        for i,timeframe in enumerate(work_hours):
            start_timeframe = as_minutes(timeframe[0])
            end_timeframe = as_minutes(timeframe[1])

            start_timeframe_week_day = timeframe[0].weekday()

            if week_day_value == start_timeframe_week_day:
                if week_day_name in work_days:
                    work_hours_temp: list = work_days[week_day_name]
                    timeframe_temp = {
                        "start": start_timeframe,
                        "end": end_timeframe
                    }
                    work_hours_temp.append(timeframe_temp)
                    work_days[week_day_name] = work_hours_temp
                else:
                    timeframe_temp = [{
                       "start": start_timeframe,
                        "end": end_timeframe
                    }]
                    work_day_temp = {
                        week_day_name: timeframe_temp
                    }
                    work_days.update(work_day_temp)

    for week_day in WeekDay:
        week_day_name = week_day.name

        if week_day_name not in work_days:
            work_day_temp = {
                week_day_name: []
            }
            work_days.update(work_day_temp)

    allowed_work_hours = json.dumps(work_days)

    return allowed_work_hours


def as_minutes(work_hour: datetime):
    hour = timedelta(hours=work_hour.hour, minutes=work_hour.minute, seconds=0)

    return int(hour.total_seconds() / 60)