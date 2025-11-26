"""
User-facing configuration base classes.
"""

import logging
import os
from typing import Any, ClassVar, List

from typedconf.config.core import ConfigLoader, load_sources
from typedconf.config.formats import TomlFileLoader
from typedconf.config.schema import Config, ConfigDict, ConfigModel, Field

logger = logging.getLogger(__name__)


class ModelConfig(ConfigModel):
    """Example of a nested configuration model."""
    id: str = Field(..., description="The model Id, like gpt-3.5-turbo")
    top_p: float = 10
    max_tokens: int = 100
    temperature: float = 0.7


class AppConfig(Config):
    """
    The base class for application configuration.

    Inherit from this class to define your application's configuration schema.
    It provides a flexible mechanism for loading settings from TOML files,
    environment variables, and other sources.
    """

    # --- Schema definition ---
    app_name: str = Field("MyCoolApp", description="Application Name")
    model: ModelConfig

    # --- Pydantic model configuration ---
    model_config = ConfigDict(
        env_prefix="APP_", env_nested_delimiter="__", case_sensitive=False
    )

    # --- Framework: Define Configuration Sources ---
    # This list can be overridden by subclasses to customize config loading.
    # The default setup implements a common pattern:
    # 1. A required base configuration file.
    # 2. An optional environment-specific file (e.g., 'config.production.toml').
    # 3. An optional local override file (for development, not in git).
    config_sources: ClassVar[List[ConfigLoader]] = []

    # --- Framework: Pydantic Integration ---

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[Config],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple[Any, ...]:
        """
        This class method is the entry point for pydantic-settings to discover
        custom configuration sources.
        """
        logger.debug("Customizing configuration sources for %s", settings_cls.__name__)

        # 1. Determine the current environment (e.g., 'development', 'production')
        # Defaults to 'development' if not set.
        env = os.getenv("APP_ENV", "development").lower()
        logger.debug("Current APP_ENV: %s", env)

        # 2. Define the file load order using the class variable
        # This makes the behavior extensible. Subclasses can just change `config_sources`.
        cls.config_sources = [
            TomlFileLoader("config.default.toml", required=True),
            TomlFileLoader(f"config.{env}.toml", required=False),
            TomlFileLoader("config.local.toml", required=False),
        ]

        # 3. Use the helper to load and merge all file-based sources
        merged_file_config = load_sources(cls.config_sources)

        # 4. Return all sources to Pydantic.
        # The order determines priority (earlier sources win).
        # This setup ensures the following precedence:
        #   1. Settings passed to the constructor (`init_settings`).
        #   2. Environment variables (`env_settings`).
        #   3. Settings from a .env file (`dotenv_settings`).
        #   4. Settings from Docker secrets (`file_secret_settings`).
        #   5. Settings from the merged TOML files.
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            lambda: merged_file_config,
        )
