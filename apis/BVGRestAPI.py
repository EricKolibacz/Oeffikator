import datetime
from concurrent.futures import process

import requests

from apis.APIInterface import APIInterface


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
        response = requests.get("https://v5.bvg.transport.rest/journeys", params=params).json()
        journey = self.__process_response(response)
        journey["origin"] = {"longitude": origin["longitude"], "latitude": origin["latitude"]}
        return journey

    def __process_response(self, response):
        stopsovers = []
        for leg in response["journeys"][0]["legs"]:
            if "stopovers" in leg:
                for stop in leg["stopovers"]:
                    if stop["arrival"] != None:
                        x = stop["stop"]["location"]["longitude"]
                        y = stop["stop"]["location"]["latitude"]
                        atime = stop["arrival"][11:19].replace(":", "")
                        stopsovers.append({"longitude": x, "latitude": y, "time": atime})
        destination = response["journeys"][0]["legs"][-1]
        aTime = destination["arrival"][11:19].replace(":", "")
        destination = {
            "longitude": destination["destination"]["longitude"],
            "latitude": destination["destination"]["latitude"],
        }
        return {"origin": None, "destination": destination, "arrivalTime": aTime, "stopovers": stopsovers}
