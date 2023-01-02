"""This module includes interface which defines the broad structure for the to be implemented apis."""
import datetime
from abc import ABC, abstractmethod


class APIRequester(ABC):
    """This interface defines the basic structure for API which can query data from public transport companies."""

    def __init__(self) -> None:
        self.past_requests = []

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
    def query_location(self, query: str, amount_of_results: int) -> dict:
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
    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int) -> dict:
        """A method which queries the journey trip for a given origin, destination and start date

        Args:
            origin (dict): json dict with origin(/start) location information
            destination (dict): json dict with destination location information
            start_date (datetime): start date and time when the journey should take place
            amount_of_results (int): the number of results which should be returned, usually 1

        Returns:
            dict: a json with journes information, including most importantly the time, how lang a trip takes
        """

    def has_reached_request_limit(self) -> bool:
        """Checks if the api has reached it request limit per minute

        Returns:
            bool: true, if limit is reached, else false
        """
        while self.past_requests and datetime.datetime.now() - self.past_requests[0]["time"] > datetime.timedelta(
            seconds=60
        ):
            self.past_requests.pop(0)
        return len(self.past_requests) > self.request_rate
