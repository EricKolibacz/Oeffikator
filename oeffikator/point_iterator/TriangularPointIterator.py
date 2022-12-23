import numpy as np
from scipy.spatial import Delaunay

from oeffikator.point_iterator.PointIteratorInterface import PointIteratorInterface


class TriangularPointIterator(PointIteratorInterface):
    def __init__(self, initial_points: np.ndarray) -> None:
        if len(initial_points.shape) != 2:
            raise ValueError("We only support 2-dimensional input.")
        if initial_points.shape[0] < 3:
            raise ValueError("We need at least three values to create traignles/generate new points.")
        if initial_points.shape[1] != 2:
            raise ValueError("Second dimension should be 2.")
        self.points = initial_points

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        tri = Delaunay(self.points)
        areas = self.__get_area(self.points[tri.simplices])
        new_point = np.mean(self.points[tri.simplices][np.argpartition(areas, -1)][-1], 0)
        self.points = np.vstack([self.points, new_point])
        return new_point

    def __get_area(self, points):
        first = np.multiply(points[:, 0, 0], np.subtract(points[:, 1, 1], points[:, 2, 1]))
        second = np.multiply(points[:, 1, 0], np.subtract(points[:, 2, 1], points[:, 0, 1]))
        third = np.multiply(points[:, 2, 0], np.subtract(points[:, 0, 1], points[:, 1, 1]))
        return 0.5 * np.add(np.add(first, second), third)
