import json
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.config.wsm_logger import wsm_logger
from src.shared.enums.types import WorkDayType, WorkTimeType
from src.shared.helpers.journey import get_work_hours_quantity, get_work_day_type, today_work_time_range, \
    clean_work_timeframes, allowed_work_days_as_json, cleanup
from src.shared.models.db.models import StandardWorkHours, FlexTime
from src.shared.repository.wsm_repository import WSMRepository


class CalculateFlextimeService:
    def __init__(self, account: StandardWorkHours, session: Session):
        self._account = account
        self._session = session
        self._standard_work_time = today_work_time_range(account)
        self._account_work_hours = get_work_hours_quantity(account)
        self._account_work_day_type = get_work_day_type(account)
        self._user_timezone = ZoneInfo("America/Sao_Paulo")

    def calculate(self) -> StandardWorkHours:
        account = self._account
        timeframes = []
        formatted_work_hours = None
        wsm_logger.info(f"Starting service to calculate flex work hours for account \"{account.uid}\"")

        wsm_logger.debug(f"Standard work time range for today, start \"{self._standard_work_time[0]}\", end \"{self._standard_work_time[1]}\"")
        wsm_logger.debug(
            f"Start work hours \"{account.start_time}\", end work hours \"{account.end_time}\" for \"{account.uid}\"")
        wsm_logger.debug(
            f"Quantity of work hours daily for account \"{account.uid}\" is \"{self._account_work_hours}\" hours")
        wsm_logger.debug(
            f"Work day type for account \"{account.uid}\" is \"{self._account_work_day_type}\"")

        if account.enable:
            wsm_logger.info(f"Account {account.uid} is enabled. Calculating work hours...")
            current_work_hours = self.get_effective_work_hours()
            formatted_work_hours = self.define_work_hour_formatted(current_work_hours)
            flex_time_timeframes = self.flex_times_as_timeframes(current_work_hours)
            timeframes = cleanup(flex_time_timeframes)
            self.debug_timeframe(timeframes)
        else:
            wsm_logger.info(f"Account {account.uid} is disabled. Blocking work hours...")

        allowed_work_hours = allowed_work_days_as_json(timeframes)

        account.allowed_work_hours = allowed_work_hours
        account.formatted_work_hours = formatted_work_hours

        wsm_logger.info(f"Allowed work hours defined as {allowed_work_hours} for account {account.uid}")
        wsm_logger.debug(f"Formatted Allowed work hours defined as {formatted_work_hours} for account {account.uid}")

        wsm_logger.debug(f"Standard work hours defined successfully as \"{account.allowed_work_hours}\"")
        wsm_logger.info(f"Finishing service to calculate flex work hours for account \"{self._account.uid}\"")

        return account

    def get_effective_work_hours(self) -> list[FlexTime]:
        workhours = []
        if self._account_work_day_type == WorkDayType.DAY_SHIFT:
            workhours = self.get_effective_work_hours_for_day()
        elif self._account_work_day_type == WorkDayType.NIGHT_SHIFT:
            workhours = self.get_effective_work_hours_for_night()

        return workhours

    def get_effective_work_hours_for_day(self) -> list[FlexTime]:
        wsm_logger.info(f"Searching for work times for account \"{self._account.uid}\"")
        flex_times = list()
        today = datetime.today()
        start_time = datetime.combine(today, time(0, 0))
        end_time = datetime.combine(today, time(23, 59))

        wsm_logger.info(f"Searching for work times with start date at \"{start_time}\", and end date at \"{end_time}\" for account \"{self._account.uid}\"")

        flex_times_found = WSMRepository().get_flex_times_between_datetime(
            self._session,
            self._account.id,
            start_time,
            end_time
        )

        for flex_time in flex_times_found:
            wsm_logger.debug(f"Adding {flex_time.work_time}, work type {flex_time.work_time_type}")
            flex_times.append(flex_time)

        wsm_logger.info(
            f"Found \"{len(flex_times)}\" flex times at \"{today}\" for account \"{self._account.uid}\"")

        return flex_times


    def get_effective_work_hours_for_night(self) -> set[FlexTime]:
        pass

    def define_work_hour_formatted(self, flex_times: list[FlexTime]) -> str:
        i = 0
        time_worked = 0.0
        work_hour_in: datetime | None = None
        work_hour_out: datetime | None = None

        while i < len(flex_times):
            current = flex_times[i]
            work_hour_in = None

            if i == 0 and current.work_time_type == WorkTimeType.OUT:
                wsm_logger.debug(
                    f"Defining work hour formatted, current flex time \"{current.work_time}\", iteration {i}, has journey type \"{current.work_time_type}\". Skipping...")
                i = i + 1
                continue

            work_hour_in = current.work_time

            if (i + 1) == len(flex_times):
                work_hours_left = self._account_work_hours.total_seconds() - time_worked
                work_hour_out = work_hour_in + timedelta(seconds=work_hours_left)
            else:
                _next = flex_times[i + 1].work_time
                work_hour_out = _next
                dt = _next - work_hour_in
                time_worked += dt.total_seconds()

            i = i + 2

        wsm_logger.info(f"Work hour defined as start \"{work_hour_in}\", and \"{work_hour_out}\"")

        formatted_work_hour = {
            "start": work_hour_in.isoformat(),
            "end": work_hour_out.isoformat()
        }

        return json.dumps(formatted_work_hour)

    def flex_times_as_timeframes(self, flex_times: list[FlexTime]) -> [(FlexTime, FlexTime)]:
        i = 0
        timeframes = []
        time_worked = 0.0

        while i < len(flex_times):
            current = flex_times[i]
            wsm_logger.debug(f"Processing current flex time \"{current.work_time}\", work type \"{current.work_time_type}\", iteration {i}")

            if i == 0 and current.work_time_type == WorkTimeType.OUT:
                wsm_logger.debug(f"Current flex time \"{current.work_time}\", iteration {i}, has journey type \"{current.work_time_type}\". Skipping...")
                i = i + 1
                continue

            if (i + 1) == len(flex_times):
                wsm_logger.debug(
                    f"Current flex time \"{current.work_time}\", iteration {i}, with journey type \"{current.work_time_type}\",is the last register. Defining end work time...")
                work_hours_left = self._account_work_hours.total_seconds() - time_worked
                _next = current.work_time + timedelta(seconds=work_hours_left)
                wsm_logger.debug(
                    f"Current flex time \"{current.work_time}\", iteration {i}, with journey type \"{current.work_time_type}\", has end work time defined as \"{_next}\"")
            else:
                _next = flex_times[i + 1].work_time
                dt =  _next - current.work_time
                time_worked += dt.total_seconds()

                wsm_logger.debug(
                    f"Current flex time \"{current.work_time}\", iteration {i}, with journey type \"{current.work_time_type}\", has work time defined as \"{_next}\"")

            timeframe = (current.work_time.astimezone(self._user_timezone), _next.astimezone(self._user_timezone))
            timeframes.append(timeframe)

            wsm_logger.debug(
                f"Added new timeframes \"{timeframe}\", time worked is \"{time_worked/3600}\" hours")

            i = i + 2

        self.debug_timeframe(timeframes)

        return timeframes

    def debug_timeframe(self, timeframes: list[tuple[datetime, datetime]]):
        for timeframe in timeframes:
            timeframe1, timeframe2 = timeframe

            wsm_logger.debug(f"Start \"{timeframe1.strftime("%Y-%m-%d %H:%M:%S")}\", end \"{timeframe2.strftime("%Y-%m-%d %H:%M:%S")}\"")


