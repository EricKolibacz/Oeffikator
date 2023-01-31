import requests


class AppTestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def alive(self):
        return requests.get(f"{self.base_url}/alive", timeout=5)
