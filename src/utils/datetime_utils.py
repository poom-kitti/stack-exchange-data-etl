"""This module contain datetime utility functions."""
from datetime import datetime

import pytz


def seconds_from_utc(timezone: str) -> int:
    """Get the time difference in seconds from UTC. Will return positive
    if time is ahead of UTC; otherwise, negative.

    Example:
    >>> seconds_from_utc("Asia/Bangkok")
    25200
    """
    now = datetime.now(tz=None)
    pytz_timezone = pytz.timezone(timezone)
    time_delta_from_utc = pytz.UTC.localize(now).astimezone(pytz_timezone) - pytz_timezone.localize(now)

    return int(time_delta_from_utc.total_seconds())
