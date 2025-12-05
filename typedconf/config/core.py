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
