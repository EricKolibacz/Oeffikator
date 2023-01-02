"""This module contains all the test for the point iterators currently implemented."""
import numpy as np
import pytest
from scipy.spatial import cKDTree

from oeffikator.point_iterator.grid_point_iterator import GridPointIterator
from oeffikator.point_iterator.triangular_iterator_interface import TriangularPointIterator

BOUNDING_BOX = (0, 1, 2.5, 3.5)  # ("west", "east", "south", "north")
POINTS_PER_AXIS = 3


# Test on GridPointIterator
def test_correct_bounding_box_length_in_grid_iterator():
    """Test if the grid iterator catches a bounding box with less than 4 entries"""
    with pytest.raises(ValueError):
        GridPointIterator(BOUNDING_BOX[:3], POINTS_PER_AXIS)


def test_plausible_bounding_box_values_in_grid_iterator():
    """Test if grid iterator checks that the first value should be lower than the second (west-east)
    and the third lower than the fourth (south-north)"""
    with pytest.raises(ValueError):
        wrong_bounding_box1 = BOUNDING_BOX[0:2][::-1] + BOUNDING_BOX[2:4][::1]
        wrong_bounding_box2 = BOUNDING_BOX[0:2][::1] + BOUNDING_BOX[2:4][::-1]
        GridPointIterator(wrong_bounding_box1, POINTS_PER_AXIS)
        GridPointIterator(wrong_bounding_box2, POINTS_PER_AXIS)


def test_correct_number_of_points_per_axis_in_grid_iterator():
    """Test if the grid iterator checks that the points per axis should be larger at least 2."""
    with pytest.raises(ValueError):
        GridPointIterator(BOUNDING_BOX, 1)


def test_first_point_from_grid_point_iterator():
    """Test if the first point is correct. It should be the most western, southern point."""
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    first_point = next(point_iterator)
    assert first_point == [0, 2.5]


def test_corner_points_from_grid_point_iterator():
    """Test if the corner points are covered by the grid iterator"""
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    points = list(point_iterator)
    assert points[0] == [0, 2.5]
    assert points[2] == [0, 3.5]
    assert points[6] == [1, 2.5]
    assert points[8] == [1, 3.5]


def test_all_points_from_grid_point_iterator():
    """Test if the grid iterator gets the grid right if we want 9 points."""
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


def test_has_points_remaining():
    """Test if the grid iterator gets the grid right if we want 9 points."""
    point_iterator = GridPointIterator(BOUNDING_BOX, POINTS_PER_AXIS)
    assert point_iterator.has_points_remaining()
    _ = list(point_iterator)
    assert not point_iterator.has_points_remaining()


# Test on TriangularPointIterator

STARTING_POINTS = np.array([[0, 0], [0, 1], [1, 1]])


def test_enough_starting_points_for_triangular_point_iterator():
    """Test if the triangular iterator checks that it gets enough points (minimum three)."""
    with pytest.raises(ValueError):
        TriangularPointIterator(STARTING_POINTS[0:2, :])  # shape (2,2)


def test_minimum_two_columns_for_triangular_point_iterator():
    """Test if the triangular iterator checks that the points should have minimum 2 coordinates."""
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[1], [2], [3]]))  # shape (1,3)


def test_maximum_two_columns_for_triangular_point_iterator():
    """Test if the triangular iterator checks that the points should have maximum 2 coordinates."""
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[1, 2, 3], [2, 3, 4], [3, 4, 5]]))  # shape (3,3)


def test_too_many_dimensions_for_triangular_point_iterator():
    """Test if the triangular iterator checks that the input is 2 dimensional."""
    with pytest.raises(ValueError):
        TriangularPointIterator(np.array([[[1, 2, 3], [2, 3, 4], [3, 4, 5]]]))  # shape (1,3,3)


def test_is_iterator_for_triangular_point_iterator():
    """Test if the triangular iterator is an iterator. Should fail if '__iter__' method is missing."""
    iter(TriangularPointIterator(STARTING_POINTS))


def test_first_point_from_triangular_point_iterator():
    """Test if the center is computed via the mean"""
    point_should_be = np.mean(STARTING_POINTS, 0)
    point_iterator = TriangularPointIterator(STARTING_POINTS)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_point_for_two_triangles_from_triangular_point_iterator():
    """Test if the resulting point is in the largest triangle."""
    point_should_be = np.mean(STARTING_POINTS, 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1]], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_consective_points_from_triangular_point_iterator():
    """Test if the triangular iterator takes the second largest triangle after filling the first."""
    point_should_be = np.mean(np.append(STARTING_POINTS[1:3, :], [[1 / 3, 2 / 3]], axis=0), 0)
    new_points = np.append(STARTING_POINTS, [[1.1, 1.1]], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    next(point_iterator)
    point_is = next(point_iterator)
    np.testing.assert_array_equal(point_is, point_should_be)


def test_two_points_from_triangular_point_iterator():
    """Test if the point generator gets points right when generating two in a row."""
    extra_point = [1, 0]
    points_should_be = [[1 / 3, 1 / 3], [7 / 9, 4 / 9]]
    new_points = np.append(STARTING_POINTS, [extra_point], axis=0)
    point_iterator = TriangularPointIterator(new_points)
    points_are = [next(point_iterator) for _ in range(2)]
    np.testing.assert_almost_equal(points_are, points_should_be)


def test_smaller_triangles_for_triangular_point_iterator():
    """Test if the point distrubution over the space is actually equal.
    Here, we test if the largest distance for all points to their closest neighbour over the long term decreases.
    In other words, if for iteration i we identify the largest distance between two points to be between point k and j,
    we hope to see that this is not the case in a future iteration. Note: it could be that
    we don't catch that right after one iteration but at leaste after some (here 10) we expect to see that.
    """
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
