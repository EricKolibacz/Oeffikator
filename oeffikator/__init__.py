"""App wide parameters"""
import datetime
import logging
from importlib.metadata import version

from .requesters.bvg_rest_requester import BVGRestRequester
from .requesters.oeffi_requester import OeffiRequester
from .settings import Settings

settings = Settings()
__version__ = version("oeffikator")

logger = logging.getLogger("uvicorn")
logger.propagate = 0

requester1 = BVGRestRequester()
requesters = [requester1]

AUTHKEY = ""
if AUTHKEY != "":
    requester2 = OeffiRequester(AUTHKEY)
    requesters.append(requester2)


TRAVELLING_DAYTIME = datetime.datetime.today().replace(hour=12, minute=0, second=0) + datetime.timedelta(days=1)
while TRAVELLING_DAYTIME.weekday() != 0:
    TRAVELLING_DAYTIME += datetime.timedelta(1)


BOUNDING_BOX = (13.2756, 13.4892, 52.4677, 52.5532)
