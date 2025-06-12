import json
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.config.wsm_logger import logger as wsm_logger
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
        self._flex_times = None

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
            self._flex_times = self.get_effective_work_hours()
            formatted_work_hours = self.define_work_hour_formatted(self._flex_times)
            flex_time_timeframes = self.flex_times_as_timeframes(self._flex_times)
            timeframes = cleanup(flex_time_timeframes)
            self.debug_timeframe(timeframes)
        else:
            wsm_logger.info(f"Account {account.uid} is disabled. Blocking work hours...")

        allowed_work_hours = allowed_work_days_as_json(timeframes)

        account.allowed_work_hours = allowed_work_hours
        account.formatted_work_hours = formatted_work_hours
        account.logon_hours = self.define_logon_hours()

        wsm_logger.info(f"Allowed work hours defined as {allowed_work_hours} for account {account.uid}")
        wsm_logger.debug(f"Formatted Allowed work hours defined as {formatted_work_hours} for account {account.uid}")

        wsm_logger.debug(f"Standard work hours defined successfully as \"{account.allowed_work_hours}\"")
        wsm_logger.info(f"Finishing service to calculate flex work hours for account \"{self._account.uid}\"")

        return account

    def define_logon_hours(self) -> str:
        work_hour_in, work_hour_out = self.define_work_hour(self._flex_times)

        if work_hour_in is not None and work_hour_out is not None:
            work_hours = [(work_hour_in, work_hour_out)]
            work_hours_time_frame = cleanup(work_hours)
            self.debug_timeframe(work_hours_time_frame)

        return allowed_work_days_as_json(work_hours_time_frame)


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

    def get_total_worked_in_seconds(self, flex_times: list[FlexTime]) -> float:
        i = 0
        total_worked_hours = 0.0

        while i < len(flex_times):
            current = flex_times[i]

            if current.work_time_type == WorkTimeType.OUT:
                i += 1
                continue

            work_time_in = current.work_time

            if (i + 1) != len(flex_times):
                work_time_out = flex_times[i + 1].work_time
                dt = work_time_out - work_time_in
                total_worked_hours += dt.total_seconds()

            i += 1

        wsm_logger.info(f"User {self._account.uid} has been worked a total of \"{total_worked_hours/3600}\" hour(s)")

        return total_worked_hours

    def define_work_hour(self, flex_times: list[FlexTime]) -> tuple[(datetime | None), (datetime | None)]:
        work_hour_in: datetime | None = None
        work_hour_out: datetime | None = None

        if len(flex_times) > 0:
            first_work_time = flex_times[0]
            last_work_time = flex_times[-1]

            work_hour_in = first_work_time.work_time

            total_worked_seconds = self.get_total_worked_in_seconds(flex_times)
            total_worked_left = self._account_work_hours.total_seconds() - total_worked_seconds

            if len(flex_times) == 1:
                work_hour_out = work_hour_in + timedelta(seconds=total_worked_left)
            else:
                if last_work_time.work_time_type == WorkTimeType.OUT:
                    work_hour_out = work_hour_in + timedelta(seconds=self._account_work_hours.total_seconds())
                else:
                    work_hour_out = last_work_time.work_time + timedelta(seconds=total_worked_left)
        else:
            wsm_logger.info(f"No flex times was found for account {self._account.uid}")

        wsm_logger.debug(f"Work hour IN defined as : {work_hour_in}")
        wsm_logger.debug(f"Work hour OUT defined as : {work_hour_out}")

        return work_hour_in, work_hour_out

    def define_work_hour_formatted(self, flex_times: list[FlexTime]) -> str:
        formatted_work_hour = {}
        work_hour_in, work_hour_out = self.define_work_hour(flex_times)

        if work_hour_in is not None and work_hour_out is not None:
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

            timeframe = (current.work_time, _next)
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


