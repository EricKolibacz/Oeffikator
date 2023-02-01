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


def test_creating_location():
    """Test whether the oeffikator can create (/post) a location properly
    (by returning the correct address and coordinates)"""
    location_description = "Alexanderplatz 1"
    expected_location = Location(
        address="10178 Berlin-Mitte, Alexanderplatz 1",
        geom="POINT (13.412904 52.521149)",
        id=-1,
        request_id=-1,
    )
    response = client.post_location(location_description)

    assert response.status_code == 200

    respons_location = Location(**response.json())
    assert respons_location.address == expected_location.address
    assert respons_location.geom == expected_location.geom
