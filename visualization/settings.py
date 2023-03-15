"""Implements the settings for the oeffikator container"""
from pydantic import BaseSettings


# pylint: disable=R0903,R0801
class Settings(BaseSettings):
    """Settings for the oeffikator container, mainly secrets"""

    app_container_name: str = "0.0.0.0"
    max_west: float = 13.243
    max_east: float = 13.51
    max_south: float = 52.44
    max_north: float = 52.567

    class Config:
        """Defines the source for the settings"""

        env_prefix = "OEFFI_"
