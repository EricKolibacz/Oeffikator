from aiohttp import ClientTimeout

"""This module contains requester specific functions and constants"""
RESPONSE_TIMEOUT = ClientTimeout(total=15)  # in seconds
