"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
from fastapi import Depends, FastAPI, Response
from sqlalchemy.orm import Session

from . import __version__, logger, requesters
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
    """Get trip durations from certain origin

    Args:
        origin_description (str): description of the trip's starting point

    Returns:
        list[schemas.Trip]: trips information (origin, destinations and durations)
    """
    logger.info("Using origin with following description: %s", location_description)
    db_location = crud.get_location_by_alias(database, location_description)
    if db_location is not None:
        # db_location.geom = to_shape(db_location.geom).wkt
        logger.info("Location is already known:")
        logger.info("  Address: %s", db_location.address)
        logger.info("  Coordinates: %s", db_location.geom)
        return db_location
    logger.info("Location description not known")

    requested_location = requesters[0].query_location(location_description)
    location = schemas.LocationCreate(
        address=requested_location["address"],
        geom=f"POINT({requested_location['longitude']} {requested_location['latitude']})",
    )
    db_location = crud.get_location_by_address(database, location.address)
    if db_location is not None:
        # db_location.geom = to_shape(db_location.geom).wkt
        logger.info("Address of Location is already known:")
        logger.info("  Address: %s", db_location.address)
        logger.info("  Coordinates: %s", db_location.geom)
        logger.info("Saving alias")
        crud.create_alias(database, schemas.LocationAliasCreate(address_alias=location_description), db_location.id)
        # db_location.geom = to_shape(db_location.geom).wkt
        return db_location
    logger.info("Address not known")

    logger.info("Saving address")
    db_location = crud.create_location(database, location)
    logger.info("Saving alias")
    crud.create_alias(database, schemas.LocationAliasCreate(address_alias=location_description), db_location.id)
    # db_location.geom = to_shape(db_location.geom).wkt
    logger.info("New Location saved:")
    logger.info("  Address: %s", db_location.address)
    logger.info("  Coordinates: %s", db_location.geom)
    return db_location


@app.get("/location/", response_model=schemas.Location | None)
def get_location(location_description: str, database: Session = Depends(get_db)) -> schemas.Location:
    """Get trip durations from certain origin

    Args:
        origin_description (str): description of the trip's starting point

    Returns:
        list[schemas.Trip]: trips information (origin, destinations and durations)
    """
    logger.info("Using origin with following description: %s", location_description)
    db_location = crud.get_location_by_alias(database, location_description)
    return db_location
