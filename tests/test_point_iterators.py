import numpy as np

from oeffikator.point_iterator.GridPointIterator import GridPointIterator
from oeffikator.point_iterator.TriangularPointIterator import TriangularPointIterator

BOUNDING_BOX = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")


# Test on GridPointIterator
def test_first_point_from_grid_point_iterator():
    grid_point_iterator = GridPointIterator(BOUNDING_BOX)
    first_point = next(grid_point_iterator)
    assert first_point == [0, 2.5]


def test_corner_points_from_grid_point_iterator():
    grid_point_iterator = GridPointIterator(BOUNDING_BOX)
    points = [point for point in grid_point_iterator]
    assert points[0] == [0, 2.5]
    assert points[2] == [0, 3.5]
    assert points[6] == [1, 2.5]
    assert points[8] == [1, 3.5]


def test_all_points_from_grid_point_iterator():
    grid_point_iterator = GridPointIterator(BOUNDING_BOX)
    points = [point for point in grid_point_iterator]
    assert points[0] == [0, 2.5]
    assert points[1] == [0, 3.0]
    assert points[2] == [0, 3.5]
    assert points[3] == [0.5, 2.5]
    assert points[4] == [0.5, 3.0]
    assert points[5] == [0.5, 3.5]
    assert points[6] == [1, 2.5]
    assert points[7] == [1, 3.0]
    assert points[8] == [1, 3.5]


# Test on TriangularPointIterator

STARTING_POINTS = np.array([[0, 0], [0, 1], [1, 1]])


def test_first_point_from_triangular_point_iterator():
    # also test if the compute center works properly
    point_should_be = np.mean(STARTING_POINTS, 0)
    grid_point_iterator = TriangularPointIterator(STARTING_POINTS)
    point_is = next(grid_point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_point_for_two_triangles_from_triangular_point_iterator():
    point_should_be = np.mean(STARTING_POINTS, 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1]], axis=0)
    grid_point_iterator = TriangularPointIterator(new_points)
    point_is = next(grid_point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_consective_points_from_triangular_point_iterator():
    point_should_be = np.mean(np.append(STARTING_POINTS[1:3, :], [[1 / 3, 2 / 3]], axis=0), 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1.1]], axis=0)
    grid_point_iterator = TriangularPointIterator(new_points)
    next(grid_point_iterator)
    point_is = next(grid_point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_points_from_triangular_point_iterator():
    extra_point = [1, 0]
    points_should_be = [[1 / 3, 1 / 3], [7 / 9, 4 / 9]]
    new_points = np.append(STARTING_POINTS, [extra_point], axis=0)
    grid_point_iterator = TriangularPointIterator(new_points)
    points_are = [next(grid_point_iterator) for _ in range(2)]
    np.testing.assert_almost_equal(points_are, points_should_be)
