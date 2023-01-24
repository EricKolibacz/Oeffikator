"""App wide parameters"""
import logging
from importlib.metadata import version

__version__ = version("oeffikator")

logger = logging.getLogger("uvicorn")
logger.propagate = 0
