"""Module which combines everything connected to the requesters"""
import datetime

from shapely import from_wkt
from sqlalchemy.orm import Session

from oeffikator import TRAVELLING_DAYTIME
from oeffikator.requesters.requester_interface import RequesterInterface

from .requesters.bvg_rest_requester import BVGRestRequester
from .requesters.oeffi_requester import OeffiRequester
from .sql_app import crud, models, schemas

requester1 = BVGRestRequester()
REQUESTERS = [requester1]

AUTHKEY = ""
if AUTHKEY != "":
    requester2 = OeffiRequester(AUTHKEY)
    REQUESTERS.append(requester2)


def get_requester() -> RequesterInterface:
    """Simple function to get an available requester (=one which hasn't reached its request limit yet)

    Raises:
        ModuleNotFoundError: raises if no requester is available
        (most probably because all have reached their request limit)

    Returns:
        RequesterInterface: an available requester
    """
    available_requester = None
    for requester in REQUESTERS:
        if not requester.has_reached_request_limit():
            available_requester = requester
            break
    if available_requester is None:
        raise ModuleNotFoundError("No requester seems to be avialble. Aborting ...")
    return requester


def request_location(location_description: str, database: Session) -> schemas.LocationCreate:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        location_description (str): description of the location
        database (Session): session to connected database

    Returns:
        schemas.LocationCreate: information on the location and the corresponding request id
    """
    requester = get_requester()
    requested_location = requester.query_location(location_description)
    request = crud.create_request(database=database)
    location = schemas.LocationCreate(
        address=requested_location["address"],
        geom=f"POINT({requested_location['longitude']} {requested_location['latitude']})",
        request_id=request.id,
    )
    return location


def request_trip(origin: models.Location, destination: models.Location, database: Session) -> dict:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        location_description (str): description of the location
        database (Session): session to connected database

    Raises:
        ModuleNotFoundError: raises if no requester is available
        (most probably because all have reached their request limit)

    Returns:
        dict: information on the location and the corresponding request id
    """
    requester = get_requester()
    requested_trip = requester.get_journey(
        convert_location_to_requesters_dict(origin),
        convert_location_to_requesters_dict(destination),
        TRAVELLING_DAYTIME,
    )
    arrivale_time = datetime.datetime.strptime(requested_trip["arrivalTime"], "%H%M%S").time()
    arrivale_time = datetime.datetime.combine(TRAVELLING_DAYTIME.date(), arrivale_time)
    duration = (arrivale_time - TRAVELLING_DAYTIME).total_seconds() / 60  # in minutes
    request = crud.create_request(database=database)

    trip = schemas.TripCreate(
        duration=duration,
        origin_id=origin.id,
        destination_id=destination.id,
        request_id=request.id,
    )

    return trip


def convert_location_to_requesters_dict(location: models.Location) -> dict:
    """Convert a sqlalchemy-type location to a dict understandable by a requester

    Args:
        location (models.Location): the location returned by the database

    Returns:
        dict: understandable location by requesters
    """
    location_dict = {}
    location_dict["address"] = location.address
    location_dict["latitude"] = from_wkt(location.geom).y
    location_dict["longitude"] = from_wkt(location.geom).x

    return location_dict
