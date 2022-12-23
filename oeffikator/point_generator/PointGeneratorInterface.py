from abc import ABC, abstractmethod


class PointGeneratorInterface(ABC):
    @abstractmethod
    def get_next_point(self, *args) -> dict:
        pass

    def get_next_points(self, group_size, *args) -> dict:
        return [self.get_next_point(args) for _ in range(group_size)]
