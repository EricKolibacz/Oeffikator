"""Implements the settings for the oeffikator container"""
from pydantic import BaseSettings


# pylint: disable=R0903
class Settings(BaseSettings):
    """Settings for the oeffikator container, mainly secrets"""

    app_container_name: str = "0.0.0.0"

    class Config:
        """Defines the source for the settings"""

        env_prefix = "OEFFI_"
