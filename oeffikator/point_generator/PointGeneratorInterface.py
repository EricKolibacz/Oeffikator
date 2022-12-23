from abc import ABC, abstractmethod


class PointGeneratorInterface(ABC):
    @abstractmethod
    def get_next_point(self, *args) -> dict:
        pass

    @abstractmethod
    def get_next_points(self, group_size: int, *args) -> dict:
        pass
