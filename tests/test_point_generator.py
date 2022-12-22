import numpy as np

from oeffikator.point_generator.GridPointGenerator import GridPointGenerator
from oeffikator.point_generator.TriangularPointGenerator import TriangularPointGenerator

BOUNDING_BOX = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")


# Test on GridPointGenerator
def test_first_point_from_grid_point_generation():
    grid_point_generation = GridPointGenerator(BOUNDING_BOX)
    first_point = grid_point_generation.get_next_points(1)
    assert first_point == [[0, 2.5]]


def test_corner_points_from_grid_point_generation():
    grid_point_generation = GridPointGenerator(BOUNDING_BOX)
    points = grid_point_generation.get_next_points(9)
    assert points[0] == [0, 2.5]
    assert points[2] == [0, 3.5]
    assert points[6] == [1, 2.5]
    assert points[8] == [1, 3.5]


def test_all_points_from_grid_point_generation():
    grid_point_generation = GridPointGenerator(BOUNDING_BOX)
    points = grid_point_generation.get_next_points(9)
    assert points[0] == [0, 2.5]
    assert points[1] == [0, 3.0]
    assert points[2] == [0, 3.5]
    assert points[3] == [0.5, 2.5]
    assert points[4] == [0.5, 3.0]
    assert points[5] == [0.5, 3.5]
    assert points[6] == [1, 2.5]
    assert points[7] == [1, 3.0]
    assert points[8] == [1, 3.5]


# Test on TriangularPointGenerator

STARTING_POINTS = np.array([[0, 0], [0, 1], [1, 1]])


def test_first_point_from_triangular_point_generation():
    # also test if the compute center works properly
    point_should_be = np.mean(STARTING_POINTS, 0)
    grid_point_generation = TriangularPointGenerator()
    point_is = grid_point_generation.get_next_points(1, STARTING_POINTS)[0]
    np.testing.assert_array_equal(point_is, point_should_be)
