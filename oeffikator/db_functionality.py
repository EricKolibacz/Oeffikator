"""Functionality related to the database"""
from . import requesters


def get_location(location_description: str) -> dict:
    """Returns the coordinates (in epsg:4326) and id for a given address string

    Args:
        address (str): a string which describes the location

    Returns:
        dict: a dictionary conatining information on location description, exact address, coordinates and id
    """
    address = requesters[0].query_location(location_description)
    # TODO implement check if address exists
    # TODO if not, create location
    return {}


def query_trips(origin_location_id: int) -> dict:
    """Query trip information from the database for a given origin.

    Args:
        int: the id of the origin location

    Returns:
        dict: trips with information on the destination and the trip time
    """
    # TODO query durations from trips-table for given location id
    # TODO raise error if location id does not exist
    return {}
