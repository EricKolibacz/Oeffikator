"""This module includes interface which defines the broad structure for the to be implemented requesters."""
import datetime
from abc import ABC, abstractmethod

from aiohttp import ClientSession

from oeffikator.requesters import CHECK_FOR_REQUESTER_AVAILABILITY_IN_SECS, RESPONSE_TIMEOUT


class RequesterInterface(ABC):
    """This interface defines the basic structure for requesters
    which can query data from public transport companies."""

    def __init__(self) -> None:
        self.past_requests = []
        self.last_responding_check = datetime.datetime.now() - datetime.timedelta(
            seconds=CHECK_FOR_REQUESTER_AVAILABILITY_IN_SECS
        )
        self._is_responding = False

    @property
    def request_rate(self) -> str:
        """Defines the required variable.

        Raises:
            NotImplementedError: This variable needs to be implemented by the child class.

        Returns:
            str: The number of requests per minute
        """
        raise NotImplementedError

    @abstractmethod
    async def query_location(self, query: str, amount_of_results: int) -> dict:
        """A method which queries the location given a input string (e.g. 'Brandenburger Tor').

        Args:
            query (str): Location for which information is needed
            amount_of_results (int): The number of matches, usually 1
            has_addresses (str): should return the address
            has_stops (str): should return nearby stops
            has_poi (str): should return neaby point of interests

        Returns:
            dict: a json response with the information of the location
        """

    @abstractmethod
    async def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int) -> dict:
        """A method which queries the journey trip for a given origin, destination and start date

        Args:
            origin (dict): json dict with origin(/start) location information
            destination (dict): json dict with destination location information
            start_date (datetime): start date and time when the journey should take place
            amount_of_results (int): the number of results which should be returned, usually 1

        Returns:
            dict: a json with journes information, including most importantly the time, how lang a trip takes
        """

    async def get(self, url: str, params: tuple[tuple[str, str]]) -> dict:
        """Method to for "GET"

        Args:
            url (str): the url to call get on
            params (tuple[tuple[str, str]]): additional parameters

        Returns:
            dict: get respondse
        """
        async with ClientSession(timeout=RESPONSE_TIMEOUT) as session:
            async with session.get(url, params=params) as response:
                return await response.json(content_type=None)

    async def post(self, url: str, data: str, headers: dict[str, str]) -> dict:
        """Method to for "POST"

        Args:
            url (str): the url to call get on
            data (str): data to post
            headers (dict[str, str]): required headers

        Returns:
            dict: post response
        """
        async with ClientSession(timeout=RESPONSE_TIMEOUT) as session:
            async with session.post(url, data=data, headers=headers) as response:
                return await response.json(content_type=None)

    def has_reached_request_limit(self) -> bool:
        """Checks if the requester has reached it request limit per minute

        Returns:
            bool: true, if limit is reached, else false
        """
        while self.past_requests and datetime.datetime.now() - self.past_requests[0]["time"] > datetime.timedelta(
            seconds=60
        ):
            self.past_requests.pop(0)
        return len(self.past_requests) > self.request_rate

    def is_responding(self) -> bool:
        """A method to check if the requesters receives responses from the api.

        Returns:
            bool: true, if the api is responding
        """
        if (
            datetime.datetime.now() - self.last_responding_check
        ).total_seconds() >= CHECK_FOR_REQUESTER_AVAILABILITY_IN_SECS:
            self.last_responding_check = datetime.datetime.now()
            self._is_responding = self._check_response()
        return self._is_responding

    @abstractmethod
    def _check_response(self) -> bool:
        """A method to check if the requesters receives responses from the api.

        Returns:
            bool: true, if the api is responding
        """
