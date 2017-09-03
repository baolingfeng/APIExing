from datetime import datetime
from datetime import *

DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'

def from_unix_time(timestamp, FMT=DEFAULT_FMT):
    int_time = timestamp
    if type(int_time) == str:
        int_time = int(int_time)

    return datetime.fromtimestamp(int_time).strftime(DEFAULT_FMT)


def format_datetime(dt, FMT=DEFAULT_FMT):
    return dt.strftime(FMT)


def now(FMT=DEFAULT_FMT):
    return format_datetime(datetime.now())


def get_interval(tdelta, mode='m'):
    if mode == 'm':
        return tdelta.seconds / 60
    elif mode == 's':
        return tdelta.seconds
    elif mode == 'h':
        return tdelta.seconds / 3600
    elif mode == 'd':
        return tdelta.days
    else:
        return tdelta.microseconds


def time_diff(t1, t2, FMT=DEFAULT_FMT, mode='s'):
    tdelta = datetime.strptime(t2, FMT) - datetime.strptime(t1, FMT)
    return get_interval(tdelta, mode)

# unix timestamp


def after_time(t, interval, FMT=DEFAULT_FMT, mode='s'):
    t1 = datetime.strptime(t, FMT)

    if mode == 's':
        delta = timedelta(seconds=interval)
    elif mode == 'h':
        delta = timedelta(hours=interval)
    elif mode == 'm':
        delta = timedelta(minutes=interval)
    elif mode == 'd':
        delta = timedelta(days=interval)

    t2 = t1 + delta
    
    return format_datetime(t2, FMT)


def time_interval(dt1, dt2, mode='s'):
    if dt1 < dt2:
        return get_interval(dt2 - dt1, mode)
    else:
        return 0 - get_interval(dt1 - dt2, mode)


def time_interval_unix(t1, t2, mode='s'):
    dt1 = datetime.fromtimestamp(t1)
    dt2 = datetime.fromtimestamp(t2)

    return time_interval(dt1, dt2)


def from_now_unix(unix_time, mode='s'):
    if type(unix_time) == str:
        unix_time = int(unix_time)

    return time_interval(datetime.now(), datetime.fromtimestamp(unix_time), mode)


if __name__ == '__main__':
    # print from_unix_time('1433398870')
    # print time_diff('2015-06-04T13:19:58Z', '2015-06-04T14:18:58Z', mode='m')
    # print from_now_unix('1433398870', 'm')

    print after_time('2015-06-04T13:19:58Z', 365, mode='d')
