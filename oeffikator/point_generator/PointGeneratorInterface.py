from abc import ABC, abstractmethod


class PointGeneratorInterface(ABC):
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self) -> dict:
        pass
