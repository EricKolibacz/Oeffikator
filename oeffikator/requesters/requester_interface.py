"""This module includes interface which defines the broad structure for the to be implemented requesters."""
import datetime
from abc import ABC, abstractmethod

from oeffikator.requesters import CHECK_FOR_REQUESTER_AVAILABILITY_IN_SECS


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
