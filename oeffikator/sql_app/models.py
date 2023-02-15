"""SQLAlchemy models (or tables) of the database"""

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base

# pylint: disable=R0903,E1102


class Request(Base):
    "SQLAlchemy model for the requests table"
    __tablename__ = "requests"
    __bind_key__ = "usage"
    __table_args__ = {"schema": "usage"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, default=func.now())

    request = relationship("Location", backref=backref("request"))


class Location(Base):
    "SQLAlchemy model for the locations table"
    __tablename__ = "locations"
    __bind_key__ = "geo"
    __table_args__ = {"schema": "geo"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String)
    _geom = mapped_column("geom", Geometry("Point", 4326), nullable=False)
    request_id = Column(Integer, ForeignKey("usage.requests.id"))

    @hybrid_property
    def geom(self) -> str:
        """Converts the database geometry in WKB to WKT

        Returns:
            str: the geometry as WKT
        """
        return to_shape(self._geom).wkt

    @geom.setter
    def geom(self, geom: str):
        """Converts the WKT-type geometry to WKB

        Args:
            geom (str): the entries geometry in srid 4326
        """
        self._geom = WKTElement(geom, srid=4326)


class LocationAlias(Base):
    "SQLAlchemy model for the location aliases table"
    __tablename__ = "location_aliases"
    __bind_key__ = "geo"
    __table_args__ = {"schema": "geo"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address_alias = Column(String, unique=True)
    location_id = Column(Integer, ForeignKey("geo.locations.id"))

    locations = relationship("Location", backref=backref("alias"), foreign_keys=[location_id])


class Trip(Base):
    "SQLAlchemy model for the trips table"
    __tablename__ = "trips"
    __bind_key__ = "geo"
    __table_args__ = {"schema": "geo"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    duration = Column(Integer, nullable=False)
    origin_id = Column(Integer, ForeignKey("geo.locations.id"))
    origin = relationship("Location", backref=backref("origin"), foreign_keys=[origin_id])
    destination_id = Column(Integer, ForeignKey("geo.locations.id"))
    destination = relationship("Location", backref=backref("destination"), foreign_keys=[destination_id])
    request_id = Column(Integer, ForeignKey("usage.requests.id"))

    request = relationship("Request", backref=backref("trip"), foreign_keys=[request_id])
