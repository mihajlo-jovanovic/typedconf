import abc
import types
from pathlib import Path
from typing import Any, Mapping

# --- 1. Use tomllib (3.11+) with a fallback to tomli
try:
    import tomllib
except ImportError:
    # For Python < 3.11, use the 'tomli' package
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: For Python < 3.11 'tomli' is required.")
        raise


class ConfigLoader(abc.ABC):
    @abc.abstractmethod
    def load(self) -> Mapping[str, Any]:
        """Loads configuration from a source."""
        pass


# --- 2. The Deep Merge Utility ---


def deep_merge(source: Mapping, destination: dict) -> dict:
    """
    A simple deep merge implementation.
    Merges 'source' (read-only) into 'destination' (mutable)
    """
    for key, value in source.items():
        if (
            isinstance(value, Mapping)
            and key in destination
            and isinstance(destination[key], dict)
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
    """Loads configuration from a TOML file."""

    def __init__(self, file_path: Path | str, ignore_if_missing: bool = True):
        self.file_path = Path(file_path)
        self.ignore_if_missing = ignore_if_missing

    def load(self) -> Mapping[str, Any]:
        if not self.file_path.exists():
            if not self.ignore_if_missing:
                # Return an empty, immutable Mapping
                return types.MappingProxyType({})
            raise FileNotFoundError(f"Config file not found: {self.file_path}")

        with open(self.file_path, "rb") as f:
            data = tomllib.load(f)
            # Wrap the loaded dict in a read-only proxy
            return types.MappingProxyType(data)


# --- 4. The Framework Helper ---


def load_sources(sources: list[ConfigLoader]) -> dict[str, Any]:
    """
    Helper function to load and deep-merge all config sources.
    Load order matters: later sources override earlier ones.
    """
    print("Inside load_sources...")
    # Remains a mutable dict, as it's the accumulator
    merged_config = {}
    for loader in sources:
        try:
            # config_data is now an immutable Mapping
            config_data = loader.load()
            # Deep merge the immutable sources into our mutable dict
            merged_config = deep_merge(config_data, merged_config)
        except Exception as e:
            print(f"Warning: Failed to load config from {loader}: {e}")

    # Return a final mutable dict for BaseSettings to consume
    return merged_config
