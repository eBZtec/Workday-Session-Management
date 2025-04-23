import ntplib
import pytz
from datetime import datetime
from src.config.wsm_logger import logger
from src.config import config

class ntpTimeService():

    def __init__(self):
        """
        Initialize the proxy NTP, get the value of the env variable if it not set this use localhost

        """

    @staticmethod
    def get_ntp_time():
        try:
            client = ntplib.NTPClient()
            response = client.request(host=config.NTP_SERVER,port=config.NTP_PORT)
            return datetime.fromtimestamp(response.tx_time).replace(tzinfo=pytz.utc)
        except ntplib.NTPException as e:
            logger.error(f"Could not get NTP time: {e}")
        except Exception as e :
            logger.error(f"Unexpected error when try to get NTP time: {e}")
        return None
