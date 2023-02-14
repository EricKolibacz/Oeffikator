"""Common functionality for the api tests"""
import requests
from requests import Response


class AppTestClient:
    """A class to test the app client"""

    def __init__(self, base_url):
        self.base_url = base_url

    def alive(self) -> Response:
        """Check if the client is alive

        Returns:
            Response: requests response if the client is alive
        """
        return requests.get(f"{self.base_url}/alive", timeout=5)

    def get_location(self, location_description: str) -> Response:
        """Get a location from the app

        Args:
            location_description (str): the description of the location

        Returns:
            Response: the location including address, geometry and id
        """
        return requests.get(f"{self.base_url}/location/{location_description}", timeout=5)

    def get_trip(self, origin_id: int, destination_id: int) -> Response:
        """Get a trip from the app

        Args:
            origin_id (int): the description of the location
            destination_id (int): the description of the location

        Returns:
            Response: the trip including the duration
        """
        return requests.get(f"{self.base_url}/trip/{origin_id}/{destination_id}", timeout=5)

    def get_all_trips(self, origin_id: int) -> Response:
        """Get all trips for a given location id from the app

        Args:
            origin_id (int): the location id of the origin

        Returns:
            Response: all trips
        """
        return requests.get(f"{self.base_url}/all_trips/{origin_id}", timeout=5)

    def get_total_number_of_requests(self) -> int:
        """Get the total number of requests made so far

        Returns:
            int: the total number of requests
        """
        return requests.get(f"{self.base_url}/total-requests/", timeout=5)
