import numpy as np

from oeffikator.point_iterator.PointIteratorInterface import PointIteratorInterface


class GridPointIterator(PointIteratorInterface):
    def __init__(self, bounding_box):
        if len(bounding_box) != 4:
            raise ValueError("The bounding box should contain 4 values: east, west, south, north")
        if bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3]:
            raise ValueError(
                "The bounding box does not follow the convention: east, west, south, north "
                "(i.e. bounding_box[0] > bounding_box[1] or bounding_box[2] > bounding_box[3])"
            )
            
        self.initial_points = []
        for x in np.linspace(bounding_box[0], bounding_box[1], 3):
            for y in np.linspace(bounding_box[2], bounding_box[3], 3):
                self.initial_points.append([x, y])
        self.points_used = 0

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        if self.points_used < len(self.initial_points):
            point = self.initial_points[self.points_used]
            self.points_used += 1
        else:
            raise StopIteration("Your reached the end of the point Grid.")
        return point

    def has_points_remaining(self):
        return self.points_used < len(self.initial_points)
