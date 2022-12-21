import numpy as np
from scipy.spatial.qhull import Delaunay

from point_generator.PointGeneratorInterface import PointGeneratorInterface


class TriangularPointGenerator(PointGeneratorInterface):
    def get_next_points(self, points, group_size):
        tri = Delaunay(points)
        areas = self.__get_area(points[tri.simplices])
        tri_centers = np.mean(points[tri.simplices][np.argpartition(areas, -group_size)[-group_size:]], 1)
        return tri_centers

    def __get_area(self, points):
        first = np.multiply(points[:, 0, 0], np.subtract(points[:, 1, 1], points[:, 2, 1]))
        second = np.multiply(points[:, 1, 0], np.subtract(points[:, 2, 1], points[:, 0, 1]))
        third = np.multiply(points[:, 2, 0], np.subtract(points[:, 0, 1], points[:, 1, 1]))
        return 0.5 * np.add(np.add(first, second), third)
