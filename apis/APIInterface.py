from abc import ABC, abstractmethod


class APIInterface(ABC):
    @abstractmethod
    def query_location(query) -> dict:
        pass

    @abstractmethod
    def get_journey(self) -> dict:
        pass
