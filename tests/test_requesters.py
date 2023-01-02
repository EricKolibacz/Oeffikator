"""Tests related to the requesters."""
import datetime

import numpy as np
import pytest

from oeffikator.requesters.bvg_rest_requester import BVGRestRequester
from oeffikator.requesters.oeffi_requester import OeffiRequester


# BVG Rest requester
def test_query_location():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester()
    location = requester.query_location("Brandenburger Tor")
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


def test_get_journey():
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


def test_has_reached_limit():
    """Tests if the bvg rest requester queries the location properly"""
    requester = BVGRestRequester()
    assert not requester.has_reached_request_limit()
    _ = requester.query_location("Brandenburger Tor")
    requester.request_rate = 0
    assert requester.has_reached_request_limit()


# Oeffi requester
def test_for_empty_auth_key():
    """Check if we receive an appropriate warning if the authkey is empty."""
    authkey = ""
    with pytest.raises(ValueError):
        OeffiRequester(authkey)


def test_for_none_auth_key():
    """Check if we receive an appropriate warning if the authkey is None."""
    authkey = None
    with pytest.raises(ValueError):
        OeffiRequester(authkey)
