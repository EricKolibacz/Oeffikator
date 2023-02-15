"""The C(reate)R(ead)U(pdate)Delete functions"""
from sqlalchemy.orm import Session, aliased

from . import models, schemas


def get_location_by_alias(database: Session, alias: str) -> models.Location | None:
    """Get a location by its location description(/alias)

    Args:
        db (Session): database session
        alias (str): the location alias (/location description)

    Returns:
        models.Location: the queried location
    """
    return (
        database.query(models.Location)
        .join(models.LocationAlias)
        .filter(models.LocationAlias.address_alias == alias)
        .first()
    )


def get_location_by_address(database: Session, address: str) -> models.Location | None:
    """Get a location by its location description(/alias)

    Args:
        db (Session): database session
        alias (str): the location's address

    Returns:
        models.Location: the queried location
    """
    return database.query(models.Location).filter(models.Location.address == address).first()


def get_location_by_id(database: Session, location_id: int) -> models.Location | None:
    """Get a location by its id

    Args:
        db (Session): database session
        location_id (int): the location's id

    Returns:
        models.Location: the queried location
    """
    return database.query(models.Location).filter(models.Location.id == location_id).first()


def create_location(database: Session, location: schemas.LocationCreate) -> models.Location:
    """Get a location by its location description(/alias)

    Args:
        db (Session): database session
        location (schemas.LocationCreate): an object containing information on the location's address and coordinates

    Returns:
        models.Location: the created location with additional information on id and request_id
    """
    db_item = models.Location(address=location.address, request_id=location.request_id)
    # if not set seperately
    # causes some transformation errors between geoalchemy2.elements.wkbeelement and wkt-string
    db_item.geom = location.geom
    database.add(db_item)
    database.commit()
    database.refresh(db_item)
    return db_item


def create_alias(database: Session, alias: schemas.LocationAliasCreate, location_id: int) -> models.LocationAlias:
    """Get a location by its location description(/alias)

    Args:
        db (Session): database session
        location (schemas.LocationAliasCreate): an object containing information on the location's alias
        (/location description)
        location_id (int): the location id to which the alias connects

    Returns:
        models.LocationAlias: the created location alias with additional information on id and location_id
    """
    db_item = models.LocationAlias(**alias.dict(), location_id=location_id)
    database.add(db_item)
    database.commit()
    database.refresh(db_item)
    return db_item


def create_trip(database: Session, trip: schemas.TripCreate) -> models.Trip:
    """Create a trip given its origin and destination id

    Args:
        database (Session): the connection to the database
        trip (TripCreate): information on the trip (without database id yet)

    Returns:
        models.Trip: the created trip
    """
    db_item = models.Trip(
        duration=trip.duration,
        origin_id=trip.origin.id,
        destination_id=trip.destination.id,
        request_id=trip.request_id,
    )
    database.add(db_item)
    database.commit()
    database.refresh(db_item)
    return db_item


def get_trip(database: Session, origin_id: int, destination_id: int) -> models.Trip:
    """Get a trip by origin and destination id

    Args:
        database (Session): the connection to the database
        origin_id (int): the id of the origin location
        destination_id (int): the id of the destination location

    Returns:
        models.Trip: the trip for the desried origin and destination id
    """
    return (
        database.query(models.Trip)
        .filter(
            models.Trip.origin_id == origin_id,
            models.Trip.destination_id == destination_id,
        )
        .first()
    )


def get_all_trips(database: Session, origin_id: int) -> list[models.Trip]:
    """Get a all trips by origin id. Note: only trips which are known to the database

    Args:
        database (Session): the connection to the database
        origin_id (int): the id of the origin location

    Returns:
        list[models.Trip]: get all trips
    """
    origin = aliased(models.Location)
    destination = aliased(models.Location)
    trips = (
        database.query(models.Trip)
        .join(origin, models.Trip.origin_id == origin.id)
        .join(destination, models.Trip.destination_id == destination.id)
        .filter(models.Trip.origin_id == origin_id)
    )
    return list(trips)


def create_request(database: Session) -> models.Request:
    """Get a location by its location description(/alias)

    Args:
        db (Session): database session

    Returns:
        models.Request: the request with current date and id
    """
    db_item = models.Request()
    database.add(db_item)
    database.commit()
    database.refresh(db_item)
    return db_item


def get_number_of_total_requests(database: Session) -> int:
    """Get the number of total requests which were sent to requesters so far

    Args:
        db (Session): database session

    Returns:
        int: the total number of requests
    """
    return database.query(models.Request).count()
