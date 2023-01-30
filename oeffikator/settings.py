"""Implements the settings for the oeffikator container"""
from pydantic import BaseSettings


# pylint: disable=R0903
class Settings(BaseSettings):
    """Settings for the oeffikator container, mainly secrets"""

    db_container_name: str = ""
    db_name: str = ""
    db_user: str = ""
    db_pw: str = ""

    class Config:
        """Defines the source for the settings"""

        secrets_dir = "/run/secrets"
