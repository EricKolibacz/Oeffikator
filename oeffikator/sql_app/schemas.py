"""Pydantic database table models (and helpers)"""
from pydantic import BaseModel, ConfigDict

# pylint: disable=R0903


class RequestBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""


class RequestCreate(RequestBase):
    """Pydantic model to add attributes needed for creation"""


class Request(RequestBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    date: str
    model_config = ConfigDict(from_attributes=True)


class LocationBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    address: str
    geom: str
    request_id: int
    model_config = ConfigDict(from_attributes=True)


class LocationCreate(LocationBase):
    """Pydantic model to add attributes needed for creation"""


class Location(LocationBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    model_config = ConfigDict(from_attributes=True)


class LocationAliasBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    address_alias: str


class LocationAliasCreate(LocationAliasBase):
    """Pydantic model to add attributes needed for creation"""


class LocationAlias(LocationAliasBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    location_id: int
    model_config = ConfigDict(from_attributes=True)


class TripBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    duration: int
    origin: Location
    destination: Location
    request_id: int


class TripCreate(TripBase):
    """Pydantic model to add attributes needed for creation"""


class Trip(TripBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    model_config = ConfigDict(from_attributes=True)
