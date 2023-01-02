"""This module includes the API class for Oeffi."""
import datetime
import json
import os

import requests

from oeffikator.requesters import RESPONSE_TIMEOUT
from oeffikator.requesters.requester_interface import RequesterInterface

AUTHKEY_FILE = "AUTHKEY_OeffiRequester.txt"


class OeffiRequester(RequesterInterface):
    """An API which queries data from the Oeffi app.
    Attention: Requires a authenification key (called AUTHKEY_OeeffiAPI.txt) in the same folder as this class.

    Args:
        APIInterface: interface which defines the abstract methods and properties of an api class

    Attributes:
        request rate: the number of requests tolerated per minute
    """

    request_rate = 100

    def __init__(self):
        super().__init__()
        self.__bvg_url = "http://bvg-apps-ext.hafas.de/bin/mgate.exe/mgate.exe"
        try:
            with open(
                os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), AUTHKEY_FILE),
                encoding="UTF-8",
            ) as keyfile:
                self.__key = keyfile.read().splitlines()[0]
        except FileNotFoundError as exception:
            raise FileNotFoundError(
                "It seems like the AUTHKEY_OeffiAPI.txt does not exist. "
                "It should though to be able to use the Oeffi API."
                "Wondering where to find a key? You can find some unsecurely stored on open-source github repos."
            ) from exception

    def query_location(self, query: str, amount_of_results: int = 1) -> dict:
        raise NotImplementedError

    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int = 1) -> dict:
        start_lid = self.__get_lid(origin["longitude"], origin["latitude"])
        dest = self.__get_dest(destination["longitude"], destination["latitude"])
        ext_id = dest[0]
        dest_type = dest[1]
        resp = self.__request_data(self.__create_json_trip(start_lid, dest_type, ext_id, start_date.strftime("%Y%m%d")))
        try:
            arrival_time = resp["svcResL"][1]["res"]["outConL"][0]["arr"]["aTimeS"]
        except IndexError:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        if arrival_time is None:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        return {"origin": origin, "destination": destination, "arrivalTime": arrival_time, "stopovers": None}

    def __request_data(self, json_string: str) -> dict:
        """Request data from the API

        Args:
            json_string (str): request string

        Returns:
            dict: response dict (json)
        """
        data = json.loads(json_string)
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        response = requests.post(self.__bvg_url, data=json.dumps(data), headers=headers, timeout=RESPONSE_TIMEOUT)
        self.past_requests.append({"time": datetime.datetime.now()})
        return json.loads(response.text)

    def __get_dest(self, longitude: float, latitude: float) -> tuple:
        """Gets the response for a destination query

        Args:
            longitude (float): Longitude (in ESPG:4326)
            latitude (float): Latitude (in EPSG:4326)

        Returns:
            tuple: response tuple of destination id and type
        """
        resp = self.__request_data(self.__create_json_geo_loc(longitude, latitude))
        ext_id = resp["svcResL"][1]["res"]["locL"][0]["extId"]
        location_type = resp["svcResL"][1]["res"]["locL"][0]["type"]
        return (ext_id, location_type)

    def __get_lid(self, longitude: float, latitude: float) -> dict:
        """Gets the reponse of a lid query

        Args:
            longitude (float): Longitude (in ESPG:4326)
            latitude (float): Latitude (in EPSG:4326)

        Returns:
            dict: response json
        """
        resp = self.__request_data(self.__create_json_geo_loc(longitude, latitude))
        return resp["svcResL"][1]["res"]["locL"][0]["lid"]

    def __create_json_geo_loc(self, longitude: float, latitude: float) -> str:
        """Create the body for a geo location requests

        Args:
            longitude (float): Longitude (in ESPG:4326)
            latitude (float): Latitude (in EPSG:4326)

        Returns:
            str: body for a geo location request
        """
        return str(
            '{"auth":{"aid":'
            f'"{self.__key}"'
            ',"type":"AID"},"client":{"id":"BVG","type":"AND"},"ext":"BVG.1",'
            '"ver":"1.18","lang":"eng","svcReqL":[{"meth":"ServerInfo","req":{"getServerDateTime":true,'
            '"getTimeTablePeriod":false}},{"meth":"LocGeoPos","cfg":{"polyEnc":"GPA"},"req":{"ring":'
            '{"cCrd":{"x":'
            f"{int(float(longitude) * 10e5)}"
            ',"y":'
            f"{int(float(latitude) * 10e5)}"
            '},"maxDist":20000},"getStops":true,"getPOIs":true,"maxLoc":1}}],"formatted":false}'
        )

    def __create_json_trip(self, start_lid: str, dest_type: str, ext_id: str, start_date: str) -> str:
        """Create the body for a trip requests

        Args:
            x (float): Longitude (in ESPG:4326)
            y (float): Latitude (in EPSG:4326)
            dest_type (str):
            ext_id (str):
            start_date (str):

        Returns:
            str: body for a trip request
        """
        return str(
            '{"auth":{"aid":"'
            f"{self.__key}"
            '}","type":"AID"},"client":{"id":"BVG","type":"AND"},"ext":"BVG.1"'
            ',"ver":"1.18","lang":"eng","svcReqL":[{"meth":"ServerInfo","req":{"getServerDateTime":true,'
            '"getTimeTablePeriod":false}},{"meth":"TripSearch","cfg":{"polyEnc":"GPA"},"req":{"depLocL":'
            '[{"type":"P","lid":"'
            f"{start_lid}"
            '}"}],"arrLocL":[{"type":"'
            f"{dest_type}"
            '","extId":"'
            f"{ext_id}"
            '"}],"outDate":"'
            f"{start_date}"
            '","outTime":"120000",'
            '"outFrwd":true,"gisFltrL":[{"mode":"FB","profile":{"type":"F","linDistRouting":false,"maxdist":2000},'
            '"type":"M","meta":"foot_speed_normal"}],"getPolyline":true,"getPasslist":true,"getConGroups":false,'
            '"getIST":false,"getEco":false,"extChgTime":-1}}],"formatted":false}'
        )
