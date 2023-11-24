"""This module includes the requester class for the BVG."""
import datetime

import pytz
import requests
from aiohttp import ClientSession

from oeffikator.requesters import RESPONSE_TIMEOUT
from oeffikator.requesters.requester_interface import RequesterInterface


class RestRequester(RequesterInterface):
    """An requester querying data from the BVG/VBB/DB.
    Does not require any authentification and is able to query coordinates from location strings.

    Args:
        RequesterInterface: interface which defines the abstract methods and properties of an requester class

    Attributes:
        request rate: the number of requests tolerated per minute
    """

    request_rate = 100

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url  # https://v5.bvg.transport.rest/locations

    async def query_location(self, query: str) -> dict:
        params = (
            ("query", query),
            ("addresses", "true"),
            ("stops", "false"),
            ("poi", "false"),
        )
        try:
            response = await self.get(f"{self.url}/locations", params=params)
        except TypeError as error:
            raise TypeError(
                f"It seems that the requester is not available. The requests raised an error: {error}"
            ) from error
        self.past_requests.append({"time": datetime.datetime.now()})
        return response[0]

    async def get_journey(
        self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int = 1
    ) -> dict:
        start_date = start_date.replace(tzinfo=pytz.timezone("Europe/Budapest")).astimezone(datetime.timezone.utc)
        params = (
            ("from.address", origin["address"]),
            ("from.latitude", origin["latitude"]),
            ("from.longitude", origin["longitude"]),
            ("to.address", destination["address"]),
            ("to.latitude", destination["latitude"]),
            ("to.longitude", destination["longitude"]),
            ("departure", start_date.strftime("%Y-%m-%dT%H:00+00:00")),
            ("results", str(amount_of_results)),
            ("stopovers", "true"),
        )
        response = await self.get(f"{self.url}/journeys", params=params)
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
                            longitude = stop["stop"]["location"]["longitude"]
                            latitude = stop["stop"]["location"]["latitude"]
                            atime = stop["arrival"][11:19].replace(":", "")
                            stopsovers.append({"longitude": longitude, "latitude": latitude, "time": atime})
            destination = response["journeys"][0]["legs"][-1]
            arrival_time = destination["arrival"][11:19].replace(":", "")
            destination = {
                "longitude": destination["destination"]["longitude"],
                "latitude": destination["destination"]["latitude"],
            }
        except KeyError:
            print("Something went wrong. The response looks like: ", response)
            has_found_no_connection: bool = "msg" in response.keys() and "No connection found" in response["msg"]
            has_no_station_nearby: bool = "msg" in response.keys() and "no stations found close" in response["msg"]
            return {
                "arrivalTime": None,
                "stopovers": None,
                "noConnectionFound": has_found_no_connection,
                "noStationFoundNearby": has_no_station_nearby,
            }
        return {"arrivalTime": arrival_time, "stopovers": stopsovers}

    def _check_response(self) -> bool:
        try:
            response = requests.get(f"{self.url}/locations?query=alexanderplatz&results=1", timeout=1)
        except requests.exceptions.ReadTimeout:
            return False
        return response.status_code // 100 == 2

    async def get(self, url: str, params: tuple[tuple[str, str]]) -> dict:
        """Method to for "GET"

        Args:
            url (str): the url to call get on
            params (tuple[tuple[str, str]]): additional parameters

        Returns:
            dict: get respondse
        """
        async with ClientSession(timeout=RESPONSE_TIMEOUT) as session:
            async with session.get(url, params=params) as response:
                return await response.json(content_type=None)

    async def post(self, url: str, data: str, headers: dict[str, str]) -> dict:
        """Method to for "POST"

        Args:
            url (str): the url to call get on
            data (str): data to post
            headers (dict[str, str]): required headers

        Returns:
            dict: post response
        """
        async with ClientSession(timeout=RESPONSE_TIMEOUT) as session:
            async with session.post(url, data=data, headers=headers) as response:
                return await response.json(content_type=None)
