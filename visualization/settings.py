"""Implements the settings for the oeffikator container"""
from pydantic import BaseSettings


# pylint: disable=R0903
class Settings(BaseSettings):
    """Settings for the oeffikator container, mainly secrets"""

    app_container_name: str = "0.0.0.0"
    bounding_box: tuple = (12.929257, 13.770260, 52.327450, 52.705182)

    class Config:
        """Defines the source for the settings"""

        env_prefix = "OEFFI_"
