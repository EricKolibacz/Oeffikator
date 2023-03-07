"""Module which combines everything connected to the requesters"""
import datetime
import time

from shapely import from_wkt
from sqlalchemy.orm import Session

from oeffikator import TRAVELLING_DAYTIME
from oeffikator.requesters.requester_interface import RequesterInterface

from . import REQUESTERS, logger
from .sql_app import crud, models, schemas


def get_requester() -> RequesterInterface:
    """Simple function to get an available requester (=one which hasn't reached its request limit yet)

    Raises:
        ModuleNotFoundError: raises if no requester is available
        (most probably because all have reached their request limit)

    Returns:
        RequesterInterface: an available requester
    """
    available_requester = None
    while available_requester is None:
        for requester in REQUESTERS:
            if not requester.has_reached_request_limit():
                available_requester = requester
                break
        if available_requester is None:
            logger.info("No requester seems to be avialble. Waiting a little bit ...")
            time.sleep(5)
    return available_requester


async def request_location(location_description: str, database: Session) -> schemas.LocationCreate:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        location_description (str): description of the location
        database (Session): session to connected database

    Returns:
        schemas.LocationCreate: information on the location and the corresponding request id
    """
    requester = get_requester()
    requested_location = await requester.query_location(location_description)
    request = crud.create_request(database=database)
    location = schemas.LocationCreate(
        address=requested_location["address"],
        geom=f"POINT({requested_location['longitude']} {requested_location['latitude']})",
        request_id=request.id,
    )
    return location


async def request_trip(
    origin: models.Location, destination: models.Location, database: Session
) -> schemas.TripCreate | None:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        location_description (str): description of the location
        database (Session): session to connected database

    Raises:
        ModuleNotFoundError: raises if no requester is available
        (most probably because all have reached their request limit)

    Returns:
        schemas.TripCreate: information on the location and the corresponding request id
    """
    requester = get_requester()
    requested_trip = await requester.get_journey(
        convert_location_to_requesters_dict(origin),
        convert_location_to_requesters_dict(destination),
        TRAVELLING_DAYTIME,
    )
    request = crud.create_request(database=database)

    if ("noConnectionFound" in requested_trip.keys() and requested_trip["noConnectionFound"]) or (
        "noStationFoundNearby" in requested_trip.keys() and requested_trip["noStationFoundNearby"]
    ):  # no connection or no address was found
        trip = schemas.TripCreate(
            duration=-1,
            origin=origin,
            destination=destination,
            request_id=request.id,
        )
        return trip

    arrivale_time = datetime.datetime.strptime(requested_trip["arrivalTime"], "%H%M%S").time()
    arrivale_time = datetime.datetime.combine(TRAVELLING_DAYTIME.date(), arrivale_time)
    duration = (arrivale_time - TRAVELLING_DAYTIME).total_seconds() / 60  # in minutes

    trip = schemas.TripCreate(
        duration=duration,
        origin=origin,
        destination=destination,
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
