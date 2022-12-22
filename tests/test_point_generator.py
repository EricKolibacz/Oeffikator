from oeffikator.point_generator.GridPointGenerator import GridPointGenerator


def test_first_point_from_grid_point_generation():
    bounding_box = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")
    grid_point_generation = GridPointGenerator(bounding_box)
    first_point = grid_point_generation.get_next_points(1)
    assert first_point == [[0, 2.5]]


def test_corner_points_from_grid_point_generation():
    bounding_box = (0, 1, 2.5, 3.5)  # ("east", "west", "south", "north")
    grid_point_generation = GridPointGenerator(bounding_box)
    points = grid_point_generation.get_next_points(9)
    assert points[0] == [0, 2.5]
    assert points[2] == [0, 3.5]
    assert points[6] == [1, 2.5]
    assert points[8] == [1, 3.5]


