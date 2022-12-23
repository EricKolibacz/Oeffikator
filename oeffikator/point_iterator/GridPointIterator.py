import numpy as np

from oeffikator.point_iterator.PointIteratorInterface import PointIteratorInterface


class GridPointIterator(PointIteratorInterface):
    """Point iterator which generates points along a grid.

    Args:
        PointIteratorInterface: interface which defines abstract methods for a point iterator

    Attibutes:
        initial_points (tuple[floats]): points which form the grid and which will be iterated over
    """

    def __init__(self, bounding_box: tuple[float]):
        """
        Args:
            bounding_box (tuple[float]): a bounding box which defines the grid. It needs following format:
            east, west, south, north (i.e. bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3])

        Raises:
            ValueError: if bounding box does not contain 4 elements in the east-west-south-north format
        """
        if len(bounding_box) != 4:
            raise ValueError("The bounding box should contain 4 values: east, west, south, north")
        if bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3]:
            raise ValueError(
                "The bounding box does not follow the convention: east, west, south, north "
                "(i.e. bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3])"
            )

        self.points = []
        for x in np.linspace(bounding_box[0], bounding_box[1], 3):
            for y in np.linspace(bounding_box[2], bounding_box[3], 3):
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
