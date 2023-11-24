"""App wide parameters"""
import datetime
import logging
from importlib.metadata import version

from .requesters.rest_requester import RestRequester
from .settings import Settings

settings = Settings()
__version__ = version("oeffikator")

logger = logging.getLogger("uvicorn")
logger.propagate = 0

BVG_V6_URL_LOCAL = f"http://{settings.bvg_api_container_name}:3000"
VBB_V6_URL_LOCAL = f"http://{settings.vbb_api_container_name}:3000"
DB_V6_URL_LOCAL = f"http://{settings.db_api_container_name}:3000"

REQUESTERS = [RestRequester(url) for url in [DB_V6_URL_LOCAL, BVG_V6_URL_LOCAL, VBB_V6_URL_LOCAL]]
REQUESTERS = tuple([requester for requester in REQUESTERS if requester.is_responding()])


TRAVELLING_DAYTIME = datetime.datetime.today().replace(hour=12, minute=0, second=0) + datetime.timedelta(days=1)
while TRAVELLING_DAYTIME.weekday() != 0:
    TRAVELLING_DAYTIME += datetime.timedelta(1)
