"""Tests related to the requesters."""
import datetime

import numpy as np
import pytest

from oeffikator.requesters.bvg_rest_requester import BVGRestRequester
from oeffikator.requesters.oeffi_requester import OeffiRequester


# BVG Rest requester
def test_query_location_for_bvg_requester():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester()
    location = requester.query_location("Brandenburger Tor")
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


def test_get_journey_for_bvg_requester():
    """Tests if the bvg rest requester gets a journey properly.
    Here, we check a trip between S+U Alexanderplatz Bhf (Berlin) and S+U Berlin Hauptbahnhof for the next weekday.
    This will fail as soon as if there are constructions on this line!"""
    time_should_be = 10

    date_today = datetime.datetime.today()
    date_next_monday = date_today + datetime.timedelta(days=-date_today.weekday(), weeks=1)

    requester = BVGRestRequester()
    origin = requester.query_location("10178 Berlin-Mitte, Alexanderplatz 1")
    destination = requester.query_location("10557 Berlin-Moabit, Europaplatz 1")

    journey = requester.get_journey(origin=origin, destination=destination, start_date=date_next_monday)
    time_is = (int(journey["arrivalTime"]) - 120000) / 100

    assert time_should_be == time_is


def test_catch_wrong_requests_for_wrong_journey_for_bvg_requester():
    """Tests if the bvg rest requester catches wrong get_journey request"""
    origin = {"address": "", "latitude": -1, "longitude": -1}
    destination = {"address": "", "latitude": -1, "longitude": -1}
    excepted_response = {
        "arrivalTime": None,
        "stopovers": None,
        "origin": {"longitude": origin["longitude"], "latitude": origin["latitude"]},
        "destination": {"longitude": destination["longitude"], "latitude": destination["latitude"]},
    }
    requester = BVGRestRequester()
    response = requester.get_journey(origin=origin, destination=destination, start_date=datetime.datetime.today())
    assert response == excepted_response


def test_has_reached_limit_for_bvg_requester():
    """Tests if the bvg rest requester queries the location properly"""
    requester = BVGRestRequester()
    assert not requester.has_reached_request_limit()
    _ = requester.query_location("Brandenburger Tor")
    requester.request_rate = 0
    assert requester.has_reached_request_limit()


# Oeffi requester
def test_for_empty_auth_key_for_oeffi_requester():
    """Check if we receive an appropriate warning if the authkey is empty."""
    authkey = ""
    with pytest.raises(ValueError):
        OeffiRequester(authkey)


def test_for_none_auth_key_for_oeffi_requester():
    """Check if we receive an appropriate warning if the authkey is None."""
    authkey = None
    with pytest.raises(ValueError):
        OeffiRequester(authkey)
