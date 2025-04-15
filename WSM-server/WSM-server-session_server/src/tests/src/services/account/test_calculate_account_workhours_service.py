from datetime import time

from src.services.account.utils.calculate_account_workhours_service import CalculateWorkhoursService


def test_calculate_unrestricted_user():
    uid = "jmichel"
    city = 2
    start_work_hour = time(8, 30)
    end_work_hour = time(17, 30)
    week_work_days = "0000010"

    calculate = CalculateWorkhoursService(
        uid,
        start_work_hour,
        end_work_hour,
        city,
        week_work_days,
        True
    )
    calculate.calculate()
