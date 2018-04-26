from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta


class DateHandler:

    @staticmethod
    def get_datetime_now():
        return dt.now(tz.utc).strftime("%Y%m%dT%H%M%S%fZ")

    @staticmethod
    def is_older_than_days(date, days):
        delta=timedelta(days)
        return dt.strptime(date,"%Y%m%dT%H%M%S%fZ")+delta < dt.now()