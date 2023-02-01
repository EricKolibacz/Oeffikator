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

    def post_location(self, location_description: str) -> Response:
        """Post a location to the app

        Args:
            location_description (str): the description of the location

        Returns:
            Response: the location including address, geometry and id
        """
        return requests.post(f"{self.base_url}/location/{location_description}", timeout=5)
