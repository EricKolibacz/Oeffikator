"""This module includes interface which defines the broad structure for the to be implemented requesters."""

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

from oeffikator.requesters.requester_interface import RequesterInterface


class GeopyLocationRequester(RequesterInterface):
    """This requester can transform coordinates into addresses."""

    request_rate = 60

    async def query_address_from_coordinates(self, latitude: float, longitude: float) -> list[str]:
        """A method which queries the location given coordinates.

        Args:
            latitude (float): latitude of location
            longitude (float): longitude of location


        Returns:
            list: address
        """
        async with Nominatim(
            user_agent="oeffikator",
            adapter_factory=AioHTTPAdapter,
        ) as geolocator:
            location = await geolocator.reverse(f"{latitude}, {longitude}")
        return location.address

    def _check_response(self) -> bool:
        return True
