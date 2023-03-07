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

BVG_V5_URL = "https://v5.bvg.transport.rest"
BVG_V6_URL = "https://v6.bvg.transport.rest"
VBB_V6_URL = "https://v6.vbb.transport.rest"

REQUESTERS = [BVGRestRequester(url) for url in [BVG_V5_URL, BVG_V6_URL, VBB_V6_URL]]

AUTHKEY = ""
if AUTHKEY != "":
    requester = OeffiRequester(AUTHKEY)
    REQUESTERS.append(requester)


TRAVELLING_DAYTIME = datetime.datetime.today().replace(hour=12, minute=0, second=0) + datetime.timedelta(days=1)
while TRAVELLING_DAYTIME.weekday() != 0:
    TRAVELLING_DAYTIME += datetime.timedelta(1)


BOUNDING_BOX = (13.2756, 13.4892, 52.4677, 52.5532)
