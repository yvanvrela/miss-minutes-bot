import datetime
import os
import requests

# 5 min in seconds
SECONDS_PER_SEGMENT = 300


def str_to_date(date_string: str):
    date = date_string.replace('-', ',').replace(':',
                                                 ',').replace('.', ',').replace(' ', ',').split(',')
    date = [int(i) for i in date]
    return datetime.datetime(*date)


def hour_to_microseconds(hour) -> int:
    hour_parts = str(hour).split(':')
    return (int(
        hour_parts[0])*3600000) + (int(hour_parts[1])*60000) + int(float(hour_parts[2])*1000)


def hour_to_seconds(hour: datetime.datetime) -> int:
    hour_parts = str(hour).split(':')
    return (int(
            hour_parts[0])*3600) + (int(hour_parts[1])*60) + int(float(hour_parts[2]))


def date_to_epoch(date: datetime.datetime) -> int:
    return int(datetime.datetime.timestamp(date) * 1000)


def hour_worked(start_date: datetime.datetime) -> datetime.timedelta:
    stop_time_now = datetime.datetime.now()
    time_worked = stop_time_now - start_date
    return time_worked


def seconds_rounded(hours_second: int) -> int:
    hour_rounded = round(hours_second / SECONDS_PER_SEGMENT)
    if hour_rounded < 1:
        return SECONDS_PER_SEGMENT
    return hour_rounded * SECONDS_PER_SEGMENT
