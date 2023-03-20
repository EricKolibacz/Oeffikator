"""Common parameters useable by the tests"""
import datetime

TRAVELLING_DAYTIME = datetime.datetime.today().replace(hour=12, minute=0, second=0) + datetime.timedelta(days=1)
while TRAVELLING_DAYTIME.weekday() != 0:
    TRAVELLING_DAYTIME += datetime.timedelta(1)
