"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
import asyncio

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Response
from shapely import from_wkt
from sqlalchemy.orm import Session

from oeffikator.point_iterator.grid_point_iterator import GridPointIterator
from oeffikator.point_iterator.triangular_iterator_interface import TriangularPointIterator
from oeffikator.requests import request_location, request_trip

from . import BOUNDING_BOX, __version__, logger
from .sql_app import crud, models, schemas
from .sql_app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)
# create App
app = FastAPI(
    title="Oeffikator",
    version=__version__,
)


@app.get("/alive", status_code=200)
async def get_service_status() -> Response:
    """Simple service alive request

    Returns:
        Response: the response to the alive statement with current version
    """
    return {"status": "ok", "version": __version__}


@app.put("/trips/{origin_description}", response_model=list[schemas.Trip])
async def requests_trips(
    origin_description: str, number_of_trips: int = 1, database: Session = Depends(get_db)
) -> list[schemas.Trip]:
    """Requests the creation of a number of trips for a given location

    Args:
        origin_description (str): description of the location
        number_of_trips (int): number of requested trips

    Returns:
        a list of trips with information on the duration, origin and destination
    """
    origin = await get_location(origin_description, database)
    known_trips = get_all_trips(origin.id, database)
    if len(known_trips) < 9:
        iterator = GridPointIterator(BOUNDING_BOX, points_per_axis=3)
    else:
        iterator = TriangularPointIterator(
            np.array(
                [
                    [float(from_wkt(trip.destination.geom).x), float(from_wkt(trip.destination.geom).y)]
                    for trip in known_trips
                ],
            )
        )
    new_trips = []
    while len(new_trips) < number_of_trips and iterator.has_points_remaining():
        tasks = []
        while iterator.has_points_remaining() and len(tasks) + len(new_trips) < number_of_trips:
            destination_coordiantes = next(iterator)
            tasks.append(
                asyncio.ensure_future(get_trip_from_coordinates(origin, known_trips, destination_coordiantes, database))
            )
        tmp_trips = await asyncio.gather(*tasks)
        logger.info(tmp_trips)
        new_trips += [trip for trip in tmp_trips if trip is not None]
        logger.info(len(new_trips))
    logger.info([trip.duration for trip in new_trips])
    return new_trips


async def get_trip_from_coordinates(
    origin: schemas.Location, known_trips: list[schemas.Trip], destination_coordiantes: np.ndarray, database: Session
) -> schemas.Trip | None:
    """Get the trip only given the coordinates of the destination

    Args:
        origin (schemas.Location): origin of the trip
        known_trips (list[schemas.Trip]): already known trips
        destination_coordiantes (np.ndarray): coordinates of the destination
        database (Session): database

    Returns:
        schemas.Trip | None: _description_
    """
    logger.info(
        "Computing new trip for destination coordinates %f, %f",
        destination_coordiantes[0],
        destination_coordiantes[1],
    )

    destination = await get_location(f"{destination_coordiantes[0]} {destination_coordiantes[1]}", database)

    if destination.geom not in [trip.destination.geom for trip in known_trips]:
        try:
            new_trip = await get_trip(origin.id, destination.id, database)
        except HTTPException:
            logger.info("Trip is not computable. Skipping this location.")
        else:
            return new_trip
    return None


@app.get("/location/{location_description}", response_model=schemas.Location | None)
async def get_location(location_description: str, database: Session = Depends(get_db)) -> schemas.Location:
    """Get location for given description. If not known yet, a location will be created.

    Args:
        origin_description (str): description of the location

    Returns:
        Location information like address of coordinates
    """
    location_description = location_description.lower()
    logger.info("Using origin with following description: %s", location_description)
    db_location = crud.get_location_by_alias(database, location_description)

    if db_location is None:
        logger.info("Location description not known")
        location = await request_location(location_description, database)
        db_location = crud.get_location_by_address(database, location.address)

        if db_location is None:
            logger.info("Address of Location not known")
            logger.info("Saving address")
            db_location = crud.create_location(database, location)
        else:
            logger.info("Address of Location is already known. No location created.")

        logger.info("Saving alias")
        crud.create_alias(database, schemas.LocationAliasCreate(address_alias=location_description), db_location.id)
    else:
        logger.info("Location description is already known. No location created.")

    logger.info("Returning:")
    logger.info("  - Address: %s", db_location.address)
    logger.info("  - Coordinates: %s", db_location.geom)
    return db_location


@app.get("/trip/{origin_id}/{destination_id}", response_model=schemas.Trip | None)
async def get_trip(origin_id: int, destination_id: int, database: Session = Depends(get_db)) -> schemas.Trip | None:
    """Get trip duration for a trip from the origin to the destination

    Args:
        origin_id (int): location id of the origin
        destination_id (int): location id of the destination

    Returns:
        a trip with information on the duration, origin and destination
    """
    origin = crud.get_location_by_id(database, origin_id)
    if origin is None:
        raise HTTPException(status_code=422, detail=f"The location id of the origin ({origin_id}) is not known")
    destination = crud.get_location_by_id(database, destination_id)
    if destination is None:
        raise HTTPException(
            status_code=422, detail=f"The location id of the destination ({destination_id}) is not known"
        )
    logger.info("Found follwing addresses:")
    logger.info("  - Origin:      %s", origin.address)
    logger.info("  - Destination: %s", destination.address)

    logger.info("Checking if trip exists in database")
    trip = crud.get_trip(database, origin_id, destination_id)
    if trip is not None:
        logger.info("Trip already in database")
    else:
        logger.info("Requesting trip time computation")
        requested_trip = await request_trip(origin, destination, database)
        if requested_trip is not None:
            logger.info("Creating trip")
            trip = crud.create_trip(database, requested_trip)
        else:
            logger.info("Trip is not available")
            raise HTTPException(
                status_code=500,
                detail="It wasn't possible to successfully request a trip for the given origin -> destination.",
            )

    return trip


@app.get("/all_trips/{origin_id}", response_model=list[schemas.Trip])
def get_all_trips(origin_id: int, database: Session = Depends(get_db)) -> list[schemas.Trip]:
    """Get all trip durations for an origin

    Args:
        origin_id (int): location id of the origin

    Returns:
        a list of trips with information on the duration, origin and destination
    """
    origin = crud.get_location_by_id(database, origin_id)
    if origin is None:
        raise HTTPException(status_code=422, detail=f"The location id of the origin ({origin_id}) is not known")

    logger.info("Found follwing addresses:")
    logger.info("  - Origin:      %s", origin.address)

    logger.info("Getting all known trips")
    trips = crud.get_all_trips(database, origin_id)

    return trips


@app.get("/total-requests/", status_code=200)
def get_total_number_of_requests(database: Session = Depends(get_db)) -> Response:
    """Check how many requests where made up to this point

    Returns:
        Response: the response to the alive statement with current version
    """
    return {"number_of_total_requests": crud.get_number_of_total_requests(database)}
