"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
import datetime

from fastapi import Depends, FastAPI, HTTPException, Response
from shapely import from_wkt
from sqlalchemy.orm import Session

from . import TRAVELLING_DAYTIME, __version__, logger, requesters
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


@app.post("/location/", response_model=schemas.Location | None)
def create_location(location_description: str, database: Session = Depends(get_db)) -> schemas.Location:
    """Create a location for a given string. If the location description or the corresponding address is known,
    no new location is created. Alias for location descriptions are updated.

    Args:
        origin_description (str): description of the location

    Returns:
        Location information like address of coordinates
    """
    logger.info("Using origin with following description: %s", location_description)
    db_location = crud.get_location_by_alias(database, location_description)

    if db_location is None:
        logger.info("Location description not known")
        requested_location = requesters[0].query_location(location_description)
        location = schemas.LocationCreate(
            address=requested_location["address"],
            geom=f"POINT({requested_location['longitude']} {requested_location['latitude']})",
        )
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


@app.get("/location/", response_model=schemas.Location | None)
def get_location(location_description: str, database: Session = Depends(get_db)) -> schemas.Location:
    """Get location for given description

    Args:
        origin_description (str): description of the location

    Returns:
        Location information like address of coordinates
    """
    logger.info("Using origin with following description: %s", location_description)
    db_location = crud.get_location_by_alias(database, location_description)
    return db_location


@app.post("/trip/", response_model=schemas.Trip | None)
def create_trip(origin_id: int, destination_id: int, database: Session = Depends(get_db)) -> schemas.Trip | None:
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

    logger.info("Requesting trip time computation")
    requested_trip = requesters[0].get_journey(
        convert_location_to_requesters_dict(origin),
        convert_location_to_requesters_dict(destination),
        TRAVELLING_DAYTIME,
    )
    duration = (
        datetime.datetime.combine(
            TRAVELLING_DAYTIME.date(), datetime.datetime.strptime(requested_trip["arrivalTime"], "%H%M%S").time()
        )
        - TRAVELLING_DAYTIME
    ).total_seconds() / 60
    logger.info("The trip takes %.2f minutes", duration)

    logger.info("Creating trip")
    trip = crud.create_trip(database, origin_id, destination_id, duration)
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
