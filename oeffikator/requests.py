"""Module which combines everything connected to the requesters"""
import asyncio
import copy
import datetime
import time
from random import shuffle

from shapely import from_wkt
from sqlalchemy.orm import Session

from oeffikator import TRAVELLING_DAYTIME
from oeffikator.requesters.requester_interface import RequesterInterface

from . import LOCATION_REQUESTER, REQUESTERS, logger
from .sql_app import crud, models, schemas

# pylint: disable-msg=W0511


async def get_requester() -> RequesterInterface:
    """Simple function to get an available requester (=one which hasn't reached its request limit yet)

    Raises:
        ModuleNotFoundError: raises if no requester is available
        (most probably because all have reached their request limit)

    Returns:
        RequesterInterface: an available requester
    """
    available_requester = None
    requesters_shuffeld = list(copy.deepcopy(REQUESTERS))
    shuffle(requesters_shuffeld)
    for _ in range(12):
        for requester in requesters_shuffeld:
            if not requester.has_reached_request_limit():
                available_requester = requester
                break
        if available_requester is None:
            logger.info("No requester seems to be avialble. Waiting a little bit ...")
            time.sleep(1)
    if available_requester is None:
        raise ValueError("No requesters are available at the moment.")
    return available_requester


async def request_location(location_description: str, database: Session) -> schemas.LocationCreate:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        location_description (str): description of the location
        database (Session): session to connected database

    Returns:
        schemas.LocationCreate: information on the location and the corresponding request id
    """
    requester = await get_requester()
    requested_location = await requester.query_location(location_description)
    request = crud.create_request(database=database)
    location = schemas.LocationCreate(
        address=requested_location["address"],
        geom=f"POINT({requested_location['longitude']} {requested_location['latitude']})",
        request_id=request.id,
    )
    return location


async def request_location_by_coordinates(
    latitude: float, longitude: float, database: Session
) -> schemas.LocationCreate:
    """A function for querying location address, coordinates, etc. for given description

    Args:
        latitude (float): latitude of the location
        longitude (float): longitude of the location
        database (Session): session to connected database

    Returns:
        schemas.LocationCreate: information on the location and the corresponding request id
    """
    while LOCATION_REQUESTER.has_reached_request_limit():
        await asyncio.sleep(1)
    address = await LOCATION_REQUESTER.query_address_from_coordinates(latitude=latitude, longitude=longitude)
    request = crud.create_request(database=database)
    location = schemas.LocationCreate(
        address=address,
        geom=f"POINT({longitude} {latitude})",
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
    requester = await get_requester()
    requested_trip = await requester.get_journey(
        convert_location_to_requesters_dict(origin),
        convert_location_to_requesters_dict(destination),
        TRAVELLING_DAYTIME,
    )
    request = crud.create_request(database=database)

    if (
        ("noConnectionFound" in requested_trip.keys() and requested_trip["noConnectionFound"])
        or ("noStationFoundNearby" in requested_trip.keys() and requested_trip["noStationFoundNearby"])
        or requested_trip["arrivalTime"] is None
    ):  # no connection or no address was found
        trip = schemas.TripCreate(
            duration=-1,
            origin=origin,
            destination=destination,
            request_id=request.id,
        )
        return trip
    arrivale_time = datetime.datetime.strptime(requested_trip["arrivalTime"], "%H%M%S").time()
    # TODO replace this hacky fix of adding one hour to the output. Why does this return an hour of difference
    arrivale_time = datetime.datetime.combine(TRAVELLING_DAYTIME.date(), arrivale_time) + datetime.timedelta(hours=1)
    duration = int((arrivale_time - TRAVELLING_DAYTIME).total_seconds() / 60)  # in minutes

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
