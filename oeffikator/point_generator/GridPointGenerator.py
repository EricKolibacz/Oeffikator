import numpy as np

from oeffikator.point_generator.PointGeneratorInterface import PointGeneratorInterface


class GridPointGenerator(PointGeneratorInterface):
    def __init__(self, bounding_box):
        self.initial_points = []
        for x in np.linspace(bounding_box[0], bounding_box[1], 3):
            for y in np.linspace(bounding_box[2], bounding_box[3], 3):
                self.initial_points.append([x, y])
        self.points_used = 0

    def get_next_point(self):
        if self.points_used < len(self.initial_points):
            point = self.initial_points[self.points_used]
            self.points_used += 1
        else:
            # TODO this seems odd - maybe a iterator is better choice
            raise IndexError("Your reached the end of the point Grid. For now, you will get an error for doing so.")
        return [point]

    def get_next_points(self, group_size):
        return [self.get_next_point()[0] for _ in range(group_size)]

    def has_points_remaining(self):
        return self.points_used < len(self.initial_points)

    def reset(self):
        self.points_used = 0
