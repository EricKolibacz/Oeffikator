import numpy as np

from oeffikator.point_iterator.PointIteratorInterface import PointIteratorInterface


class GridPointIterator(PointIteratorInterface):
    """Point iterator which generates points along a grid.

    Args:
        PointIteratorInterface: interface which defines abstract methods for a point iterator

    Attibutes:
        points (tuple[floats]): points which form the grid and which will be iterated over
    """

    def __init__(self, bounding_box: tuple[float], points_per_axis: int):
        """
        Args:
            bounding_box (tuple[float]): a bounding box which defines the grid. It needs following format:
            east, west, south, north (i.e. bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3])
            points_per_axis (int): the number of points for both axis, e.g. if 3, 3*3 points will be generated

        Raises:
            ValueError: if bounding box does not contain 4 elements in the east-west-south-north format
            or if the points per axis is lower than 2 (which is the minimum)
        """
        if len(bounding_box) != 4:
            raise ValueError("The bounding box should contain 4 values: east, west, south, north")
        if bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3]:
            raise ValueError(
                "The bounding box does not follow the convention: east, west, south, north "
                "(i.e. bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3])"
            )
        if points_per_axis < 2:
            raise ValueError(
                "point_per_axis parameter is too low (<2). At least 2 points are required."
                " See documentation for details"
            )

        self.points = []
        for x in np.linspace(bounding_box[0], bounding_box[1], points_per_axis):
            for y in np.linspace(bounding_box[2], bounding_box[3], points_per_axis):
                self.points.append([x, y])
        self.points_used = 0

    def __iter__(self):
        return self

    def __next__(self) -> list:
        if self.points_used < len(self.points):
            point = self.points[self.points_used]
            self.points_used += 1
        else:
            raise StopIteration("Your reached the end of the point Grid.")
        return point

    def has_points_remaining(self) -> bool:
        """Method to check if the end of the iterator is reached

        Returns:
            bool: true, if the end is reached, else flase
        """
        return self.points_used < len(self.points)
