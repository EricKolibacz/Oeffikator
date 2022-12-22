from abc import ABC, abstractmethod


class PointGeneratorInterface(ABC):
    @abstractmethod
    def get_next_points(self, group_size, *args) -> dict:
        pass
