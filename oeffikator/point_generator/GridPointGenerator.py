import numpy as np

from oeffikator.point_generator.PointGeneratorInterface import PointGeneratorInterface


class GridPointGenerator(PointGeneratorInterface):
    def __init__(self, bounding_box):
        self.initial_points = []
        for x in np.linspace(bounding_box[0], bounding_box[1], 3):
            for y in np.linspace(bounding_box[2], bounding_box[3], 3):
                self.initial_points.append([x, y])
        self.points_used = 0

    def get_next_points(self, group_size):
        if self.points_used + group_size < len(self.initial_points):
            index_group_end = self.points_used + group_size
        else:
            index_group_end = len(self.initial_points)
        point_group = self.initial_points[self.points_used : index_group_end]
        self.points_used = index_group_end
        return point_group

    def has_points_remaining(self):
        return self.points_used < len(self.initial_points)

    def reset(self):
        self.points_used = 0
