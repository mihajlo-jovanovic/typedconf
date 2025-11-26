"""
Core components for loading and merging configuration data.
"""
import abc
import logging
import types
from pathlib import Path
from typing import Any, Mapping

# --- 0. Setup Logging ---
logger = logging.getLogger(__name__)

# --- 1. Use tomllib (3.11+) with a fallback to tomli ---
try:
    import tomllib
except ImportError:
    # For Python < 3.11, use the 'tomli' package
    try:
        import tomli as tomllib
    except ImportError:
        logger.error("For Python < 3.11, the 'tomli' package is required for TOML parsing.")
        raise


class ConfigLoader(abc.ABC):
    """Abstract base class for all configuration loaders."""

    @abc.abstractmethod
    def load(self) -> Mapping[str, Any]:
        """
        Loads configuration from a source and returns it as a read-only mapping.
        If the source cannot be loaded, it should return an empty mapping.
        """
        pass


# --- 2. The Deep Merge Utility ---


def deep_merge(source: Mapping, destination: dict) -> dict:
    """
    Recursively merges a 'source' mapping into a 'destination' dictionary.

    - If a key exists in both and both values are mappings, it recurses.
    - If a key in source has a dict value and the destination does not, it copies the dict.
    - Otherwise, it overwrites the destination value with the source value.

    Args:
        source: The mapping to merge from (read-only).
        destination: The dictionary to merge into (mutable).

    Returns:
        The mutated destination dictionary.
    """
    for key, value in source.items():
        if (
            isinstance(value, Mapping)
            and key in destination
            and isinstance(destination.get(key), dict)
        ):
            # Recurse if both source and dest have dict-like value
            deep_merge(value, destination[key])
        elif isinstance(value, dict):
            # If source has a dict and value doesn't, copy it
            destination[key] = value.copy()
        else:
            destination[key] = value
    return destination


# --- 3. Concrete Loader Implementation (TOML) ---


class TomlFileLoader(ConfigLoader):
    """
    Loads configuration from a TOML file.
    """

    def __init__(self, file_path: Path | str, required: bool = False):
        """
        Initializes the loader.

        Args:
            file_path: The path to the TOML file.
            required: If True, a FileNotFoundError will be raised if the file doesn't exist.
                      If False, a missing file will be silently ignored.
        """
        self.file_path = Path(file_path)
        self.required = required

    def load(self) -> Mapping[str, Any]:
        """
        Loads the TOML file.

        Returns:
            A read-only mapping of the configuration data.

        Raises:
            FileNotFoundError: If the file is 'required' and does not exist.
        """
        if not self.file_path.exists():
            if self.required:
                raise FileNotFoundError(f"Required config file not found: {self.file_path}")
            logger.debug(f"Optional config file not found, skipping: {self.file_path}")
            return types.MappingProxyType({})

        try:
            with open(self.file_path, "rb") as f:
                data = tomllib.load(f)
                logger.debug(f"Successfully loaded config from {self.file_path}")
                # Wrap the loaded dict in a read-only proxy to enforce immutability
                return types.MappingProxyType(data)
        except (tomllib.TOMLDecodeError, OSError) as e:
            logger.warning(f"Failed to load or parse TOML file {self.file_path}: {e}")
            return types.MappingProxyType({})

    def __repr__(self) -> str:
        return f"TomlFileLoader(file_path='{self.file_path}', required={self.required})"


# --- 4. The Framework Helper ---


def load_sources(sources: list[ConfigLoader]) -> dict[str, Any]:
    """
    Helper function to load and deep-merge all config sources.
    Load order matters: later sources in the list will override earlier ones.
    """
    logger.debug(f"Loading configuration from {len(sources)} sources...")
    merged_config = {}
    for loader in sources:
        try:
            config_data = loader.load()
            # Deep merge the immutable sources into our mutable dict
            merged_config = deep_merge(config_data, merged_config)
        except Exception as e:
            logger.error(f"Unexpected error loading config from {loader}: {e}", exc_info=True)

    logger.debug("Finished loading and merging all sources.")
    # Return a final mutable dict for BaseSettings to consume
    return merged_config
