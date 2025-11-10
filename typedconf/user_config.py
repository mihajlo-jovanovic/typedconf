from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from typedconf.config import TomlFileLoader, load_sources


class ModelConfig(BaseModel):
    id: str = Field(..., description="The model Id, like gpt-3.5-turbo")
    top_p: int = 10


class AppConfig(BaseSettings):
    # --- Schema definition ---
    app_name: str = Field("MyCoolApp", description="Application Name")
    model: ModelConfig

    # --- Pydantic-Settings Configuration
    model_config = SettingsConfigDict(
        env_prefix="APP_", env_nested_delimiter="__", case_sensitive=False
    )

    # --- Framework integration ---
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple[Any, ...]:
        print("DEBUG: settings_customise_sources CALLED")
        # 1. Define the file load order
        file_sources = [
            TomlFileLoader("config.default.toml", False),
            TomlFileLoader("config.prod.toml"),
            TomlFileLoader("config.local.toml"),
        ]

        # 2. Use the helper
        merged_file_config = load_sources(file_sources)

        # 3. Wrap in callable and return custom source along with default sources
        # Order matters: earlier sources have HIGHER priority (first-wins)
        # So for "last-wins" behavior as described in README, we reverse the order
        return (env_settings, init_settings, lambda: merged_file_config)
