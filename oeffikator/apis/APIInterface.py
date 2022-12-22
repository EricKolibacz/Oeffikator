import datetime
from abc import ABC, abstractmethod


class APIInterface(ABC):
    def __init__(self) -> None:
        self.past_requests = []

    @property
    def request_rate(self) -> str:
        """
        :return: The number of requests per minute
        """
        raise NotImplementedError

    @abstractmethod
    def query_location(
        self, query: str, amount_of_results=1, has_addresses="true", has_stops="false", has_poi="false"
    ) -> dict:
        pass

    @abstractmethod
    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results=1) -> dict:
        pass

    def has_reached_request_limit(self) -> bool:
        while self.past_requests and datetime.datetime.now() - self.past_requests[0]["time"] > datetime.timedelta(
            seconds=60
        ):
            self.past_requests.pop(0)
        return len(self.past_requests) > self.request_rate
