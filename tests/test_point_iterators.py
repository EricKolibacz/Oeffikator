import numpy as np
import pytest
from scipy.spatial import cKDTree

from oeffikator.point_iterator.GridPointIterator import GridPointIterator
from oeffikator.point_iterator.TriangularPointIterator import TriangularPointIterator

BOUNDING_BOX = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")
POINTS_PER_AXIS = 3


# Test on GridPointIterator
def test_correct_bounding_box_length_in_grid_iterator():
    with pytest.raises(ValueError):
        GridPointIterator(BOUNDING_BOX[:3], POINTS_PER_AXIS)


def test_plausible_bounding_box_values_in_grid_iterator():
    with pytest.raises(ValueError):
        wrong_bounding_box1 = BOUNDING_BOX[0:2][::-1] + BOUNDING_BOX[2:4][::1]
        wrong_bounding_box2 = BOUNDING_BOX[0:2][::1] + BOUNDING_BOX[2:4][::-1]
        GridPointIterator(wrong_bounding_box1, POINTS_PER_AXIS)
        GridPointIterator(wrong_bounding_box2, POINTS_PER_AXIS)


def test_correct_number_of_points_per_axis_in_grid_iterator():
    with pytest.raises(ValueError):
        GridPointIterator(BOUNDING_BOX, 1)


def test_first_point_from_grid_point_iterator():
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    first_point = next(point_iterator)
    assert first_point == [0, 2.5]


def test_corner_points_from_grid_point_iterator():
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    points = list(point_iterator)
    assert points[0] == [0, 2.5]
    assert points[2] == [0, 3.5]
    assert points[6] == [1, 2.5]
    assert points[8] == [1, 3.5]


def test_all_points_from_grid_point_iterator():
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    points = list(point_iterator)
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


def test_enough_starting_points_for_triangular_point_iterator():  # at least 2 rows
    with pytest.raises(ValueError):
        TriangularPointIterator(STARTING_POINTS[0:2, :])  # shape (2,2)


def test_minimum_two_columns_for_triangular_point_iterator():
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[1], [2], [3]]))  # shape (1,3)


def test_maximum_two_columns_for_triangular_point_iterator():
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[1, 2, 3], [2, 3, 4], [3, 4, 5]]))  # shape (3,3)


def test_too_many_dimensions_for_triangular_point_iterator():
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[[1, 2, 3], [2, 3, 4], [3, 4, 5]]]))  # shape (1,3,3)


def test_first_point_from_triangular_point_iterator():
    # also test if the compute center works properly
    point_should_be = np.mean(STARTING_POINTS, 0)
    point_iterator = TriangularPointIterator(STARTING_POINTS)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_point_for_two_triangles_from_triangular_point_iterator():
    point_should_be = np.mean(STARTING_POINTS, 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1]], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_consective_points_from_triangular_point_iterator():
    point_should_be = np.mean(np.append(STARTING_POINTS[1:3, :], [[1 / 3, 2 / 3]], axis=0), 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1.1]], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    next(point_iterator)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_points_from_triangular_point_iterator():
    extra_point = [1, 0]
    points_should_be = [[1 / 3, 1 / 3], [7 / 9, 4 / 9]]
    new_points = np.append(STARTING_POINTS, [extra_point], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    points_are = [next(point_iterator) for _ in range(2)]
    np.testing.assert_almost_equal(points_are, points_should_be)


def test_smaller_triangles_for_triangular_point_iterator():
    point_iterator = TriangularPointIterator(np.array(STARTING_POINTS))
    largest_distance_for_current_points = []
    for _ in range(10):  # iterator over (10-1=)9 points
        tree = cKDTree(point_iterator.points, leafsize=100)
        distance_to_farthest_neighbour_in_neighbourhood = [
            np.max(tree.query(item, k=2)[0]) for item in point_iterator.points
        ]
        # find the overall/global largest distance for all points to their closest neighbour
        largest_distance_for_current_points.append(np.max(distance_to_farthest_neighbour_in_neighbourhood))
        next(point_iterator)
    assert largest_distance_for_current_points == sorted(largest_distance_for_current_points, reverse=True)
    assert largest_distance_for_current_points[0] > largest_distance_for_current_points[-1]
