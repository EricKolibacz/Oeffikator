from oeffikator.point_generator.GridPointGenerator import GridPointGenerator

BOUNDING_BOX = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")


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
