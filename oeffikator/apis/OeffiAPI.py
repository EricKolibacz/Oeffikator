"""This module includes the API class for Oeffi."""
import datetime
import json
import os

import requests

from oeffikator.apis import RESPONSE_TIMEOUT
from oeffikator.apis.APIInterface import APIInterface

AUTHKEY_FILE = "AUTHKEY_OeffiAPI.txt"


class OeffiAPI(APIInterface):
    """An API which queries data from the Oeffi app.
    Attention: Requires a authenification key (called AUTHKEY_OeeffiAPI.txt) in the same folder as this class.

    Args:
        APIInterface: interface which defines the abstract methods and properties of an api class

    Attributes:
        request rate: the number of requests tolerated per minute
    """

    request_rate = 100

    def __init__(self):
        super(OeffiAPI, self).__init__()
        self.__BVG_URL = "http://bvg-apps-ext.hafas.de/bin/mgate.exe/mgate.exe"
        with open(
            os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), AUTHKEY_FILE),
            encoding="UTF-8",
        ) as keyfile:
            self.__key = keyfile.read().splitlines()[0]

    def query_location(
        self,
        query: str,
        amount_of_results: int = 1,
        has_addresses: str = "true",
        has_stops: str = "false",
        has_poi: str = "false",
    ) -> dict:
        raise NotImplementedError

    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results: int = 1) -> dict:
        start_lid = self.__get_lid(origin["longitude"], origin["latitude"])
        dest = self.__get_dest(destination["longitude"], destination["latitude"])
        extId = dest[0]
        dest_type = dest[1]
        resp = self.__request_data(self.__create_JSON_TRIP(start_lid, dest_type, extId, start_date.strftime("%Y%m%d")))
        try:
            aTime = resp["svcResL"][1]["res"]["outConL"][0]["arr"]["aTimeS"]
        except IndexError:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        if aTime is None:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        return {"origin": origin, "destination": destination, "arrivalTime": aTime, "stopovers": None}

    def __request_data(self, json_string: str) -> dict:
        """Request data from the API

        Args:
            json_string (str): request string

        Returns:
            dict: response dict (json)
        """
        data = json.loads(json_string)
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        r = requests.post(self.__BVG_URL, data=json.dumps(data), headers=headers, timeout=RESPONSE_TIMEOUT)
        self.past_requests.append({"time": datetime.datetime.now()})
        return json.loads(r.text)

    def __get_dest(self, x: float, y: float) -> tuple:
        """Gets the response for a destination query

        Args:
            x (float): Longitude (in ESPG:4326)
            y (float): Latitude (in EPSG:4326)

        Returns:
            tuple: response tuple of destination id and type
        """
        resp = self.__request_data(self.__create_JSON_GEOLOC(x, y))
        e = resp["svcResL"][1]["res"]["locL"][0]["extId"]
        t = resp["svcResL"][1]["res"]["locL"][0]["type"]
        return (e, t)

    def __get_lid(self, x: float, y: float) -> dict:
        """Gets the reponse of a lid query

        Args:
            x (float): Longitude (in ESPG:4326)
            y (float): Latitude (in EPSG:4326)

        Returns:
            dict: response json
        """
        resp = self.__request_data(self.__create_JSON_GEOLOC(x, y))
        return resp["svcResL"][1]["res"]["locL"][0]["lid"]

    def __create_JSON_GEOLOC(self, x: float, y: float) -> str:
        """Create the body for a geo location requests

        Args:
            x (float): Longitude (in ESPG:4326)
            y (float): Latitude (in EPSG:4326)

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
            f"{int(float(x) * 10e5)}"
            ',"y":'
            f"{int(float(y) * 10e5)}"
            '},"maxDist":20000},"getStops":true,"getPOIs":true,"maxLoc":1}}],"formatted":false}'
        )

    def __create_JSON_TRIP(self, start_lid: str, dest_type: str, extId: str, start_date: str) -> str:
        """Create the body for a trip requests

        Args:
            x (float): Longitude (in ESPG:4326)
            y (float): Latitude (in EPSG:4326)

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
            f"{extId}"
            '"}],"outDate":"'
            f"{start_date}"
            '","outTime":"120000",'
            '"outFrwd":true,"gisFltrL":[{"mode":"FB","profile":{"type":"F","linDistRouting":false,"maxdist":2000},'
            '"type":"M","meta":"foot_speed_normal"}],"getPolyline":true,"getPasslist":true,"getConGroups":false,'
            '"getIST":false,"getEco":false,"extChgTime":-1}}],"formatted":false}'
        )
