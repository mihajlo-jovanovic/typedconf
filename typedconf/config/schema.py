"""
Facade classes that wrap Pydantic to decouple users from direct Pydantic dependency.
This allows the library to change its internal implementation without breaking user code.
"""

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field as PydanticField
from pydantic import ValidationError as PydanticValidationError
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict as PydanticSettingsConfigDict


class ConfigModel(PydanticBaseModel):
    """
    Base class for configuration model schemas.

    Users should extend this class for nested configuration objects.
    This is a facade over Pydantic's BaseModel.
    """
    pass


class Config(PydanticBaseSettings):
    """
    Base class for top-level configuration with automatic environment variable support.

    Users should extend this class for their main configuration class.
    This is a facade over Pydantic's BaseSettings.
    """
    pass


class ConfigDict(PydanticSettingsConfigDict):
    """
    Configuration dictionary for settings behavior.

    This is a facade over Pydantic's SettingsConfigDict.
    """
    pass


# Re-export common types so users don't need to import from Pydantic
Field = PydanticField
ValidationError = PydanticValidationError


__all__ = ["ConfigModel", "Config", "ConfigDict", "Field", "ValidationError"]
