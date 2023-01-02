"""Tests related to the requesters."""
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
