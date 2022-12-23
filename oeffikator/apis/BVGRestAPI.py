import datetime

import requests

from oeffikator.apis import RESPONSE_TIMEOUT
from oeffikator.apis.APIInterface import APIInterface


class BVGRestAPI(APIInterface):
    """An API querying data from the BVG.
    Does not require any authentification and is able to query coordinates from location strings.

    Args:
        APIInterface: interface which defines the abstract methods and properties of an api class

    Attributes:
        request rate: the number of requests tolerated per minute
    """

    request_rate = 100

    def query_location(self, query: str, amount_of_results: int = 1) -> dict:
        params = (
            ("query", query),
            ("results", str(amount_of_results)),
            ("addresses", "true"),
            ("stops", "false"),
            ("poi", "false"),
        )
        response = requests.get(
            "https://v5.bvg.transport.rest/locations", params=params, timeout=RESPONSE_TIMEOUT
        ).json()[0]
        self.past_requests.append({"time": datetime.datetime.now()})
        return response

    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int = 1) -> dict:
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
        response = requests.get(
            "https://v5.bvg.transport.rest/journeys", params=params, timeout=RESPONSE_TIMEOUT
        ).json()
        self.past_requests.append({"time": datetime.datetime.now()})
        journey = self.__process_response(response)
        journey["origin"] = {"longitude": origin["longitude"], "latitude": origin["latitude"]}
        journey["destination"] = {
            "longitude": float(destination["longitude"]),
            "latitude": float(destination["latitude"]),
        }
        return journey

    def __process_response(self, response: dict) -> dict:
        """Method to standardize the api response and make it usable

        Args:
            response (dict): api respons (as json)

        Returns:
            dict: json which is simpler to handle and process
        """
        stopsovers = []
        try:
            for leg in response["journeys"][0]["legs"]:
                if "stopovers" in leg:
                    for stop in leg["stopovers"]:
                        if stop["arrival"] is not None:
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
        except KeyError:
            print("Something went wrong. The response looks like: ", response)
            return {"arrivalTime": None, "stopovers": None}
        return {"arrivalTime": aTime, "stopovers": stopsovers}
