"""Tests related to the requesters."""
import asyncio
import datetime
import random

import numpy as np
import pytest

from oeffikator.requesters.bvg_rest_requester import BVGRestRequester
from oeffikator.requesters.oeffi_requester import OeffiRequester

BVG_V5_URL = "https://v5.bvg.transport.rest"
BVG_V6_URL = "https://v6.bvg.transport.rest"
VBB_V6_URL = "https://v6.vbb.transport.rest"

URL = random.choice([BVG_V5_URL, BVG_V6_URL, VBB_V6_URL])


# BVG Rest requester
def test_bvg5_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester(BVG_V5_URL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# BVG Rest requester
def test_bvg6_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester(BVG_V6_URL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# BVG Rest requester
def test_vbb6_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester(VBB_V6_URL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# BVG Rest requester
def test_query_location_for_bvg_requester():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = BVGRestRequester(URL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


def test_get_journey_for_bvg_requester():
    """Tests if the bvg rest requester gets a journey properly.
    Here, we check a trip between S+U Alexanderplatz Bhf (Berlin) and S+U Berlin Hauptbahnhof for the next weekday.
    This will fail as soon as if there are constructions on this line!"""
    time_should_be = (10, 11)  # apparently, bvg apis return slightly different values for different versions

    date_today = datetime.datetime.today()
    date_next_monday = date_today + datetime.timedelta(days=-date_today.weekday(), weeks=1)

    requester = BVGRestRequester(URL)
    origin = asyncio.run(requester.query_location("10178 Berlin-Mitte, Alexanderplatz 1"))
    destination = asyncio.run(requester.query_location("10557 Berlin-Moabit, Europaplatz 1"))

    journey = asyncio.run(requester.get_journey(origin=origin, destination=destination, start_date=date_next_monday))
    time_is = (int(journey["arrivalTime"]) - 120000) / 100

    assert time_is in time_should_be


def test_catch_wrong_requests_for_wrong_journey_for_bvg_requester():
    """Tests if the bvg rest requester catches wrong get_journey request"""
    origin = {"address": "", "latitude": -1, "longitude": -1}
    destination = {"address": "", "latitude": -1, "longitude": -1}
    excepted_response = {
        "arrivalTime": None,
        "stopovers": None,
        "origin": {"longitude": origin["longitude"], "latitude": origin["latitude"]},
        "destination": {"longitude": destination["longitude"], "latitude": destination["latitude"]},
        "noConnectionFound": False,
        "noStationFoundNearby": False,
    }
    requester = BVGRestRequester(URL)
    response = asyncio.run(
        requester.get_journey(origin=origin, destination=destination, start_date=datetime.datetime.today())
    )
    assert response == excepted_response


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


# requester interface check
def test_has_reached_limit_for_requester_interface():
    """Tests if the bvg rest requester queries the location properly"""
    requester = BVGRestRequester(URL)
    assert not requester.has_reached_request_limit()
    _ = asyncio.run(requester.query_location("Brandenburger Tor"))
    requester.request_rate = 0
    assert requester.has_reached_request_limit()


def test_if_requests_are_poped_after_timeout():
    """Tests if the bvg rest requester queries the location properly"""
    requester = BVGRestRequester(URL)
    _ = asyncio.run(requester.query_location("Brandenburger Tor"))
    requester.request_rate = 0
    assert requester.has_reached_request_limit()
    requester.past_requests[0]["time"] = datetime.datetime.now() - datetime.timedelta(seconds=61)
    assert not requester.has_reached_request_limit()
