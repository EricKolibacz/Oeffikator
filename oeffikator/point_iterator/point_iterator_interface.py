"""This modul contains the interface which defines the broad structure of the point interators."""
from abc import ABC, abstractmethod

import numpy as np


class PointIteratorInterface(ABC):
    """This interface defines the basic structure point iterator classes."""

    @abstractmethod
    def __iter__(self):
        """Python iterator specific method."""

    @abstractmethod
    def __next__(self) -> list | np.ndarray:
        """Python iterator specific method which returns the next element.

        Returns:
            list | np.ndarray: the next point in the generator
        """
