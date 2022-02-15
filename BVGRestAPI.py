import datetime

import requests

from APIInterface import APIInterface


class BVGRestAPI(APIInterface):
    def __init__(self):
        # request rate per minute
        self.request_rate = 100

    def query_location(
        self, query: str, amount_of_results=1, has_addresses="true", has_stops="false", has_poi="false"
    ) -> dict:
        params = (
            ("query", query),
            ("results", str(amount_of_results)),
            ("addresses", has_addresses),
            ("stops", has_stops),
            ("poi", has_poi),
        )
        return requests.get("https://v5.bvg.transport.rest/locations", params=params).json()[0]

    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results=1) -> dict:
        params = (
            ("from.address", origin["address"]),
            ("from.latitude", origin["latitude"]),
            ("from.longitude", origin["longitude"]),
            ("to.address", destination["address"]),
            ("to.latitude", destination["latitude"]),
            ("to.longitude", destination["longitude"]),
            ("departure", start_date.strftime("%Y-%m-%dT11:00+00:00")),
            ("results", str(amount_of_results)),
            ("stopovers", "true"),
        )
        return requests.get("https://v5.bvg.transport.rest/journeys", params=params).json()
