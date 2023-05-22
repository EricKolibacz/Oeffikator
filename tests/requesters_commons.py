"""A module for the common functions used for the requesters"""
import asyncio

import numpy as np

from oeffikator.requesters.bvg_rest_requester import BVGRestRequester


def is_alive(url: str) -> bool:
    """Tests if the requester queries the location properly"""
    coordinates_should_be = np.array([52.51627344417692, 13.37766793796735])
    if "bvg" in url or "vbb" in url:
        requester = BVGRestRequester(url)
    else:
        raise ValueError(f"The url {url} is not supported")
    try:
        location = asyncio.run(requester.query_location("Brandenburger Tor"))
    except TypeError:
        return False
    coordinates_is = np.array([location["latitude"], location["longitude"]])
    np.testing.assert_array_almost_equal(coordinates_should_be, coordinates_is, decimal=3)
    return True
