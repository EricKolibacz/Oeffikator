"""Pydantic database table models (and helpers)"""
from pydantic import BaseModel

# pylint: disable=R0903


class RequestBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""


class RequestCreate(RequestBase):
    """Pydantic model to add attributes needed for creation"""


class Request(RequestBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    date: str

    class Config:
        """For pydantic configuration"""

        orm_mode = True


class LocationBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    address: str
    geom: str
    request_id: int

    class Config:
        """For pydantic configuration"""

        orm_mode = True


class LocationCreate(LocationBase):
    """Pydantic model to add attributes needed for creation"""


class Location(LocationBase):
    """Pydantic model for adding attributes for reading"""

    id: int

    class Config:
        """For pydantic configuration"""

        orm_mode = True


class LocationAliasBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    address_alias: str


class LocationAliasCreate(LocationAliasBase):
    """Pydantic model to add attributes needed for creation"""


class LocationAlias(LocationAliasBase):
    """Pydantic model for adding attributes for reading"""

    id: int
    location_id: int

    class Config:
        """For pydantic configuration"""

        orm_mode = True


class TripBase(BaseModel):
    """Pydantic model to have common attributes while creating or reading data"""

    duration: int
    origin_id: int
    destination_id: int
    request_id: int


class TripCreate(TripBase):
    """Pydantic model to add attributes needed for creation"""


class Trip(TripBase):
    """Pydantic model for adding attributes for reading"""

    id: int

    class Config:
        """For pydantic configuration"""

        orm_mode = True
