"""Tests on the functionality of the api (and indirectly on the database too)"""
import random
import string
import time

import requests.exceptions

from oeffikator.sql_app.schemas import Location, Trip
from tests.api_commons import AppTestClient

client = AppTestClient("http://0.0.0.0:8200")
LOCATION_1 = "Alexanderplatz 1"
LOCATION_2 = "Friedrichstr. 50"
LOCATION_3 = "Unter den Linden 1"
LOCATION_COORDINATES = (
    52.509669,
    13.376294,
)  # Berlin Potsdamer Platz, Tilla-Durieux-Park, Tiergarten, Mitte, Berlin, 10785, Deutschland


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
    location_description = LOCATION_1
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
    location_description = LOCATION_1
    location_description_alias = f"Berlin {LOCATION_1}"

    response = client.get_location(location_description)
    response_alias = client.get_location(location_description_alias)

    location = Location(**response.json())
    location_alias = Location(**response_alias.json())
    assert location.id == location_alias.id


def test_location_by_coordinates():
    """Test whether the oeffikator gets the location by coorindates right"""
    response = client.get_location_from_coordinates(LOCATION_COORDINATES[0], LOCATION_COORDINATES[1])
    location = Location(**response.json())
    assert location.address == "Berlin Potsdamer Platz, Potsdamer Platz, Tiergarten, Mitte, Berlin, 10785, Deutschland"


def test_trip():
    """Test whether the oeffikator gets the trip duration properly"""
    origin_description = LOCATION_1
    destination_description = LOCATION_2
    expected_trip_duration = 14  # in minutes

    origin = Location(**client.get_location(origin_description).json())
    destination = Location(**client.get_location(destination_description).json())
    response = client.get_trip(origin.id, destination.id)

    trip = Trip(**response.json())
    assert trip.duration == expected_trip_duration


def test_trip_error_for_wrong_ids():
    """Test whether the oeffikator returns an error if the origin or destination ids are not known"""
    origin_description = LOCATION_1

    response = client.get_trip(-1, -1)
    assert response.status_code == 422
    assert "origin" in response.json()["detail"] and "not known" in response.json()["detail"]

    origin = Location(**client.get_location(origin_description).json())
    response = client.get_trip(origin.id, -1)
    assert response.status_code == 422
    assert "destination" in response.json()["detail"] and "not known" in response.json()["detail"]


def test_increasing_number_of_requests():
    """Test whether the oeffikator count of total number of requests is increasing"""
    initial_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    # create a random string, otherwise the count will not increase after rerunning the test
    # because the location alias would be already known
    random_string = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.get_location(random_string)
    post_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    assert (
        post_count == initial_count + 1
    ), "maybe random location was already known; either re-run test or re-start test service"


def test_indirectly_if_location_is_read_from_database():
    """Test whether the oeffikator requests a location (which results in an increased request count)
    or gets the location from the database"""

    random_string = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.get_location(random_string)
    initial_count = client.get_total_number_of_requests().json()["number_of_total_requests"]
    client.get_location(random_string)
    post_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    assert post_count == initial_count


def test_indirectly_if_trip_is_read_from_database():
    """Test whether the oeffikator requests a trip (which results in an increased request count)
    or gets the trip from the database"""
    origin_description = LOCATION_1
    destination_description = LOCATION_2
    origin = Location(**client.get_location(origin_description).json())
    destination = Location(**client.get_location(destination_description).json())

    client.get_trip(origin.id, destination.id)  # trip either requested or read
    initial_count = client.get_total_number_of_requests().json()["number_of_total_requests"]
    client.get_trip(origin.id, destination.id)  # trip should be read now --> no. of requests stays the same
    post_count = client.get_total_number_of_requests().json()["number_of_total_requests"]

    assert post_count == initial_count


def test_get_all_trips():
    """Test whether it is possible to get all the trips for a given origin id"""
    origin_description = LOCATION_1
    destination_description = LOCATION_2
    origin = Location(**client.get_location(origin_description).json())
    destination = Location(**client.get_location(destination_description).json())

    trip = Trip(**client.get_trip(origin.id, destination.id).json())
    trips = [Trip(**trip) for trip in client.get_all_trips(origin.id).json()]

    assert trip in trips


def test_get_all_trips_empty():
    """Test whether it is possible to get all the trips for a origin id for which there should not trips exist"""
    origin_description = LOCATION_2
    origin = Location(**client.get_location(origin_description).json())
    trips = [Trip(**trip) for trip in client.get_all_trips(origin.id).json()]

    assert not trips, f"It seems to exist trips for the location {LOCATION_2} for which no trips should be known"


def test_requesting_trips_creation():
    """Test whether it is possible to request the creation of trips for a given location"""
    origin_description = LOCATION_3
    number_of_trips = 1

    origin = Location(**client.get_location(origin_description).json())
    client.request_trips(origin.address, number_of_trips)
    time.sleep(4)
    trips = [Trip(**trip) for trip in client.get_all_trips(origin.id).json()]

    assert len(trips) == 1

    client.request_trips(origin.address, number_of_trips).json()
    time.sleep(4)
    trips = [Trip(**trip) for trip in client.get_all_trips(origin.id).json()]

    assert len(trips) == 2
