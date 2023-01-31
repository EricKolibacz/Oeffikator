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
