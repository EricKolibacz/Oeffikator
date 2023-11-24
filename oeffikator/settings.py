"""Implements the settings for the oeffikator container"""
from pydantic_settings import BaseSettings, SettingsConfigDict


# pylint: disable=R0903,R0801
class Settings(BaseSettings):
    """Settings for the oeffikator container, mainly secrets"""

    db_container_name: str = ""
    db_name: str = ""
    db_user: str = ""
    db_pw: str = ""
    bvg_api_container_name: str = "0.0.0.0"
    vbb_api_container_name: str = "0.0.0.0"
    db_api_container_name: str = "0.0.0.0"
    max_west: float = 13.2
    max_east: float = 13.55
    max_south: float = 52.42
    max_north: float = 52.59
    model_config = SettingsConfigDict(env_prefix="OEFFI_", secrets_dir="/run/secrets")
