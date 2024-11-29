import datetime
import json
from datetime import time, date

from pytz import timezone

from src.models.models import ExtendedWorkHours
from src.utils.timeframes_helper import is_time_greater_than, split_work_hour_in_two_timeframes, \
    split_work_hour_in_timeframe
from src.utils.week_day_helper import WeekDay, WorkDay


def as_minutes(work_hour: datetime.datetime):
    hour = datetime.timedelta(hours=work_hour.hour, minutes=work_hour.minute, seconds=0)

    return int(hour.total_seconds() / 60)


def string_to_time(hours: str):
    hour, minutes = hours.split(":")

    return time(int(hour), int(minutes))

def add_timezone(hour: datetime.datetime):
    return hour.astimezone(timezone("America/Sao_Paulo"))


def generate_work_hours(
        work_week_days: list[int],
        start_work_hour: time,
        end_work_hour: time
) -> list[(int, int)]:
    current_date = date.today()
    work_hours = []

    for i, work_week_day in enumerate(work_week_days):
        work_date = date.fromordinal(current_date.toordinal() + i)
        work_date_week_day = work_date.weekday()

        if work_date_week_day == WeekDay.SUNDAY:
            if work_week_days[0] == WorkDay.WORK:
                if is_time_greater_than(start_work_hour, end_work_hour):
                    first_timeframe, second_timeframe = split_work_hour_in_two_timeframes(work_date,
                                                                                               start_work_hour,
                                                                                               end_work_hour)
                    work_hours.append(first_timeframe)
                    work_hours.append(second_timeframe)
                else:
                    timeframe = split_work_hour_in_timeframe(work_date, start_work_hour, end_work_hour)
                    work_hours.append(timeframe)
        else:
            if work_week_days[work_date_week_day + 1] == WorkDay.WORK:
                if is_time_greater_than(start_work_hour, end_work_hour):
                    first_timeframe, second_timeframe = split_work_hour_in_two_timeframes(work_date,
                                                                                                start_work_hour,
                                                                                                end_work_hour)
                    work_hours.append(first_timeframe)
                    work_hours.append(second_timeframe)
                else:
                    timeframe = split_work_hour_in_timeframe(work_date, start_work_hour, end_work_hour)
                    work_hours.append(timeframe)

    return work_hours


def generate_overtime_hours(overtimes: list[ExtendedWorkHours] | None):
    overtimes_result = []

    for _, overtime in enumerate(overtimes):
        start_overtime: datetime.datetime = add_timezone(overtime.extension_start_time)
        end_overtime: datetime.datetime = add_timezone(overtime.extension_end_time)

        if start_overtime.day != end_overtime.day:
            next_day = date.fromordinal(start_overtime.toordinal() + 1)
            first_end_overtime = datetime.datetime(
                start_overtime.year,
                start_overtime.month,
                start_overtime.day,
                23,
                59,
                0,
                0,
                tzinfo=timezone("America/Sao_Paulo")
            )

            overtimes_result.append((start_overtime, first_end_overtime))

            next_start_overtime = datetime.datetime(
                next_day.year,
                next_day.month,
                next_day.day,
                0,
                0,
                0,
                0,
                tzinfo=timezone("America/Sao_Paulo")
            )
            next_end_overtime = datetime.datetime(
                end_overtime.year,
                end_overtime.month,
                end_overtime.day,
                end_overtime.hour,
                end_overtime.minute,
                0,
                0,
                tzinfo=timezone("America/Sao_Paulo")
            )

            overtimes_result.append((next_start_overtime, next_end_overtime))
        else:
            overtimes_result.append((start_overtime, end_overtime))

    return overtimes_result


def allowed_work_days_as_json(work_hours: list[tuple[datetime.datetime, datetime.datetime]]):
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

    allowed_work_hours = json.dumps(work_days)

    return allowed_work_hours