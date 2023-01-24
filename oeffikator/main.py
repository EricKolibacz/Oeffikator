"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
from fastapi import FastAPI, Response

from oeffikator.db_functionality import get_location, query_trips

from . import __version__, logger

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


@app.get("/get_trip_durations/")
async def get_trip(origin_description: str) -> Response:
    """Get trip durations from certain origin

    Args:
        origin_description (str): description of the trip's starting point

    Returns:
        Response: trips information (origin, destinations and durations)
    """
    # TODO raise error if origin_description is empty
    logger.info("Using origin with following description: %s", origin_description)
    origin = get_location(origin_description)
    logger.info("We are going to use following location:")
    logger.info("- address: %s", {origin["address"]})
    logger.info("- coordiantes: (%s, %s)", {origin["latitude"]}, {origin["longitude"]})
    trips = query_trips(origin["id"])
    return {"origin": origin, "trips": trips}
