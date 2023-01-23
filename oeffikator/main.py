"""Main module of the oeffikator app, providing the actual FastAPI / Uvicorn app."""
from fastapi import FastAPI, Response

from . import __version__

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
