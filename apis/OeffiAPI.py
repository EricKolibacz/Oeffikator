import datetime
import json
from concurrent.futures import process

import requests

from apis.APIInterface import APIInterface


class OeffiAPI(APIInterface):
    request_rate = 100

    def __init__(self):
        super(OeffiAPI, self).__init__()
        self.__BVG_URL = "http://bvg-apps-ext.hafas.de/bin/mgate.exe/mgate.exe"
        # requires key, x and y coordinates
        self.__JSON_GEOLOC = '{"auth":{"aid":"%s","type":"AID"},"client":{"id":"BVG","type":"AND"},"ext":"BVG.1","ver":"1.18","lang":"eng","svcReqL":[{"meth":"ServerInfo","req":{"getServerDateTime":true,"getTimeTablePeriod":false}},{"meth":"LocGeoPos","cfg":{"polyEnc":"GPA"},"req":{"ring":{"cCrd":{"x":%d,"y":%d},"maxDist":20000},"getStops":true,"getPOIs":true,"maxLoc":1}}],"formatted":false}'
        # requires key, start_lid, dest_type, extId
        self.__JSON_TRIP_SEARCH = '{"auth":{"aid":"%s","type":"AID"},"client":{"id":"BVG","type":"AND"},"ext":"BVG.1","ver":"1.18","lang":"eng","svcReqL":[{"meth":"ServerInfo","req":{"getServerDateTime":true,"getTimeTablePeriod":false}},{"meth":"TripSearch","cfg":{"polyEnc":"GPA"},"req":{"depLocL":[{"type":"P","lid":"%s"}],"arrLocL":[{"type":"%s","extId":"%s"}],"outDate":"%s","outTime":"120000","outFrwd":true,"gisFltrL":[{"mode":"FB","profile":{"type":"F","linDistRouting":false,"maxdist":2000},"type":"M","meta":"foot_speed_normal"}],"getPolyline":true,"getPasslist":true,"getConGroups":false,"getIST":false,"getEco":false,"extChgTime":-1}}],"formatted":false}'
        with open("AUTHKEY.txt") as keyfile:
            self.__key = keyfile.read().splitlines()[0]

    def query_location(
        self, query: str, amount_of_results=1, has_addresses="true", has_stops="false", has_poi="false"
    ) -> dict:
        return None

    def get_journey(self, origin: dict, destination: dict, start_date: datetime, amount_of_results=1) -> dict:
        start_lid = self.__get_lid(origin["longitude"], origin["latitude"])
        dest = self.__get_dest(destination["longitude"], destination["latitude"])
        extId = dest[0]
        dest_type = dest[1]
        resp = self.__request_data(
            self.__JSON_TRIP_SEARCH % (self.__key, start_lid, dest_type, extId, start_date.strftime("%Y%m%d"))
        )
        try:
            aTime = resp["svcResL"][1]["res"]["outConL"][0]["arr"]["aTimeS"]
        except:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        if aTime is None:
            return {"origin": origin, "destination": destination, "arrivalTime": None, "stopovers": None}
        return {"origin": origin, "destination": destination, "arrivalTime": aTime, "stopovers": None}

    def __process_response(self, response):
        pass

    def __request_data(self, json_string):
        data = json.loads(json_string)
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        r = requests.post(self.__BVG_URL, data=json.dumps(data), headers=headers)
        self.past_requests.append({"time": datetime.datetime.now()})
        return json.loads(r.text)

    def __get_dest(self, x, y):
        resp = self.__request_data(self.__JSON_GEOLOC % (self.__key, int(float(x) * 10e5), int(float(y) * 10e5)))
        e = resp["svcResL"][1]["res"]["locL"][0]["extId"]
        t = resp["svcResL"][1]["res"]["locL"][0]["type"]
        return (e, t)

    def __get_lid(self, x, y):
        resp = self.__request_data(self.__JSON_GEOLOC % (self.__key, int(x * 10e5), int(y * 10e5)))
        return resp["svcResL"][1]["res"]["locL"][0]["lid"]
