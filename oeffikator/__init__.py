"""App wide parameters"""
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
