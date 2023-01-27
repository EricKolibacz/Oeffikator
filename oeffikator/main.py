"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session

from oeffikator.requests import request_location, request_trip

from . import __version__, logger
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
        location = request_location(location_description, database)
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
    requested_trip = request_trip(origin, destination, database)
    logger.info("The trip takes %.2f minutes", requested_trip.duration)

    logger.info("Creating trip")
    trip = crud.create_trip(database, requested_trip)
    return trip
