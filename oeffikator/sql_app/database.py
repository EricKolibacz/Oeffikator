"""Database settings and its ORM relevant classes/instances"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from oeffikator import settings

# pylint: disable=R0903


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.db_user}:{settings.db_pw}@oeffikator-db:5432/oeffikator"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """declarative base class - SQLAlchemy-specific"""


# Dependency
def get_db():
    """Dependency, SQLAlchemy-specific helper class

    Yields:
        sessionmaker: a database session
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
