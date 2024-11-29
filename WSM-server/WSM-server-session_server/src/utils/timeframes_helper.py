import datetime
from datetime import time, timedelta, date
from operator import itemgetter

from pytz import timezone


def is_time_greater_than(start: time, end: time):
    start_timedelta = timedelta(hours=start.hour, minutes=start.minute)
    end_timedelta = timedelta(hours=end.hour, minutes=end.minute)

    return start_timedelta.total_seconds() > end_timedelta.total_seconds()


def split_work_hour_in_timeframe(day: date, start_work_hour: time, end_work_hour: time):
    start_date = datetime.datetime(
        day.year,
        day.month,
        day.day,
        start_work_hour.hour,
        start_work_hour.minute,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )
    end_date = datetime.datetime(
        day.year,
        day.month,
        day.day,
        end_work_hour.hour,
        end_work_hour.minute,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )

    return start_date, end_date


def split_work_hour_in_two_timeframes(
        day: date,
        start_work_hour: time,
        end_work_hour: time
):

    first_timeframe_start_date = datetime.datetime(
        day.year,
        day.month,
        day.day,
        start_work_hour.hour,
        start_work_hour.minute,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )

    next_day = date.fromordinal(day.toordinal() + 1)
    first_timeframe_end_date = datetime.datetime(
        next_day.year,
        next_day.month,
        next_day.day,
        0,
        0,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )

    second_timeframe_start_date = datetime.datetime(
        next_day.year,
        next_day.month,
        next_day.day,
        0,
        0,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )
    second_timeframe_end_date = datetime.datetime(
        next_day.year,
        next_day.month,
        next_day.day,
        end_work_hour.hour,
        end_work_hour.minute,
        0,
        0,
        tzinfo=timezone("America/Sao_Paulo")
    )

    first_timeframe = (first_timeframe_start_date, first_timeframe_end_date)
    second_timeframe = (second_timeframe_start_date, second_timeframe_end_date)

    return first_timeframe, second_timeframe


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