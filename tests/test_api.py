"""Tests on the functionality of the api (and indirectly on the database too)"""
import random
import string

import requests.exceptions

from oeffikator.sql_app.schemas import Location
from tests.api_commons import AppTestClient

client = AppTestClient("http://0.0.0.0:8001")


# TEST CASES: Basic API tests (how it behaves on different edge cases)


def test_alive():
    """Test whether the oeffikator is there."""
    try:
        response = client.alive()
        assert response.status_code == 200
        return
    except requests.exceptions.ConnectionError:
        pass
    # having this assert in the `except` block prints the entire stacktrace, which is confusing
    assert False, "test-app not found; start it via `docker compose up` in the tests folder"


def test_getting_location():
    """Test whether the oeffikator can get a location
    (by returning the correct address and coordinates)"""
    location_description = "Alexanderplatz 1"
    expected_location = Location(
        address="10178 Berlin-Mitte, Alexanderplatz 1",
        geom="POINT (13.412904 52.521149)",
        id=-1,
        request_id=-1,
    )
    response = client.get_location(location_description)

    assert response.status_code == 200

    response_location = Location(**response.json())
    assert response_location.address == expected_location.address
    assert response_location.geom == expected_location.geom


def test_location_alias():
    """Test whether the oeffikator assigns the same location id to for two locations with alias location descriptions"""
    location_description = "Alexanderplatz 1"
    location_description_alias = "Berlin Alexanderplatz 1"

    response = client.get_location(location_description)
    response_alias = client.get_location(location_description_alias)

    location = Location(**response.json())
    location_alias = Location(**response_alias.json())
    assert location.id == location_alias.id


def test_increasing_number_of_requests():
    """Test whether the oeffikator count of total number of requests is increasing"""
    initial_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    # create a random string, otherwise the count will not increase after rerunning the test
    # because the location alias would be already known
    random_string = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.get_location(random_string)
    post_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    assert post_count == initial_count + 1


def test_indirectly_if_location_is_read_from_database():
    """Test whether the oeffikator requests a location (which results in an increased request count)
    or gets the location from the database"""

    random_string = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.get_location(random_string)
    initial_count = client.get_total_number_of_requests().json()["number_of_total_requests"]
    client.get_location(random_string)
    post_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    assert post_count == initial_count
