import numpy as np
from scipy.spatial import Delaunay

from oeffikator.point_iterator.PointIteratorInterface import PointIteratorInterface


class TriangularPointIterator(PointIteratorInterface):
    """A point iterator which is based on the idea that one can create a set of traingles for a given list of points.
    The triangles with the largest areas indicate less dense regions of points.
    The center (=mean of the point coordinates) of teh largest traingle is returned.
    The iterator keeps track of the point list, meaning it adds each new point to the list of points.

    Args:
        PointIteratorInterface: interface which defines abstract methods for a point iterator

    Attributes:
        points (np.ndarray): All 2D points
    """

    def __init__(self, initial_points: np.ndarray) -> None:
        """

        Args:
            initial_points (np.ndarray): initial points to start of with. Since the class is based
            on the idea of triangles it requires at least three points.

        Raises:
            ValueError: initial points need to be 2-dimensional and need to be at least 3.
        """
        if len(initial_points.shape) != 2:
            raise ValueError("We only support 2-dimensional input.")
        if initial_points.shape[0] < 3:
            raise ValueError("We need at least three values to create traignles/generate new points.")
        if initial_points.shape[1] != 2:
            raise ValueError("Second dimension should be 2.")
        self.points = initial_points

    def __iter__(self):
        return self

    def __next__(self) -> np.ndarray:
        tri = Delaunay(self.points)
        areas = self.__get_area(self.points[tri.simplices])
        new_point = np.mean(self.points[tri.simplices][np.argpartition(areas, -1)][-1], 0)
        self.points = np.vstack([self.points, new_point])
        return new_point

    def __get_area(self, points: np.ndarray) -> np.ndarray:
        """Compute the area for a given set of triangles.

        Args:
            points (np.ndarray): triangles for which we need the area

        Returns:
            np.ndarray: the area for each of the given triangles
        """
        first = np.multiply(points[:, 0, 0], np.subtract(points[:, 1, 1], points[:, 2, 1]))
        second = np.multiply(points[:, 1, 0], np.subtract(points[:, 2, 1], points[:, 0, 1]))
        third = np.multiply(points[:, 2, 0], np.subtract(points[:, 0, 1], points[:, 1, 1]))
        return 0.5 * np.add(np.add(first, second), third)
