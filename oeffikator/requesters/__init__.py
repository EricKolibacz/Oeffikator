"""This module contains requester specific functions and constants"""
from aiohttp import ClientTimeout

RESPONSE_TIMEOUT = ClientTimeout(total=15)  # in seconds
