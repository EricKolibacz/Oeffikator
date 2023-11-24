"""Tests related to the requesters."""
import asyncio
import datetime
import random

import numpy as np
import pytest

from oeffikator.requesters.rest_requester import RestRequester
from tests import TRAVELLING_DAYTIME
from tests.requesters_commons import is_alive

BVG_V6_URL_LOCAL = "http://127.0.0.1:3200"
VBB_V6_URL_LOCAL = "http://127.0.0.1:3201"
DB_V6_URL_LOCAL = "http://127.0.0.1:3202"

AVAILABLE_URLS = [url for url in [BVG_V6_URL_LOCAL, VBB_V6_URL_LOCAL, DB_V6_URL_LOCAL] if is_alive(url)]

URL = random.choice(AVAILABLE_URLS) if AVAILABLE_URLS else None


# BVG Rest requester
def test_bvg6_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = RestRequester(BVG_V6_URL_LOCAL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# VBB Rest requester
def test_vbb6_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = RestRequester(VBB_V6_URL_LOCAL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# DB Rest requester
def test_db6_alive():
    """Tests if the bvg rest requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = RestRequester(DB_V6_URL_LOCAL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


# BVG Rest requester
def test_query_location_for_bvg_requester():
    """Tests if the bvg rest requester queries the location properly"""
    if URL is None:
        pytest.skip("No Requester is alive")
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    requester = RestRequester(URL)
    location = asyncio.run(requester.query_location("Brandenburger Tor"))
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)


def test_get_journey_for_bvg_requester():
    """Tests if the bvg rest requester gets a journey properly.
    Here, we check a trip between S+U Alexanderplatz Bhf (Berlin) and S+U Berlin Hauptbahnhof for the next weekday.
    This will fail as soon as if there are constructions on this line!"""
    if URL is None:
        pytest.skip("No Requester is alive")
    time_should_be = (10, 11, 12)  # apparently, bvg apis return slightly different values for different versions

    requester = RestRequester(URL)
    origin = asyncio.run(requester.query_location("10178 Berlin-Mitte, Alexanderplatz 1"))
    destination = asyncio.run(requester.query_location("10557 Berlin-Moabit, Europaplatz 1"))

    journey = asyncio.run(requester.get_journey(origin=origin, destination=destination, start_date=TRAVELLING_DAYTIME))
    time_is = (int(journey["arrivalTime"]) - ((TRAVELLING_DAYTIME.hour - 1) * 10000)) / 100

    assert time_is in time_should_be


def test_catch_wrong_requests_for_wrong_journey_for_bvg_requester():
    """Tests if the bvg rest requester catches wrong get_journey request"""
    if URL is None:
        pytest.skip("No Requester is alive")
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
    requester = RestRequester(URL)
    response = asyncio.run(
        requester.get_journey(origin=origin, destination=destination, start_date=datetime.datetime.today())
    )
    assert response == excepted_response




# requester interface check
def test_has_reached_limit_for_requester_interface():
    """Tests if the bvg rest requester queries the location properly"""
    if URL is None:
        pytest.skip("No Requester is alive")
    requester = RestRequester(URL)
    assert not requester.has_reached_request_limit()
    _ = asyncio.run(requester.query_location("Brandenburger Tor"))
    requester.request_rate = 0
    assert requester.has_reached_request_limit()


def test_if_requests_are_poped_after_timeout():
    """Tests if the bvg rest requester queries the location properly"""
    if URL is None:
        pytest.skip("No Requester is alive")
    requester = RestRequester(URL)
    _ = asyncio.run(requester.query_location("Brandenburger Tor"))
    requester.request_rate = 0
    assert requester.has_reached_request_limit()
    requester.past_requests[0]["time"] = datetime.datetime.now() - datetime.timedelta(seconds=61)
    assert not requester.has_reached_request_limit()
