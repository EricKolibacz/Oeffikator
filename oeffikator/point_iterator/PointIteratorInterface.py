from abc import ABC, abstractmethod

import numpy as np


class PointIteratorInterface(ABC):
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self) -> list | np.ndarray:
        pass
