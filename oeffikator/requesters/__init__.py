"""This module contains requester specific functions and constants"""
from aiohttp import ClientTimeout

RESPONSE_TIMEOUT = ClientTimeout(total=60)  # in seconds
CHECK_FOR_REQUESTER_AVAILABILITY_IN_SECS = 1 * 24 * 60 * 60  # once per day
