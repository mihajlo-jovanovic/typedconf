"""
Configuration file formats and loaders.
"""
import logging
import types
from pathlib import Path
from typing import Any, Mapping

from typedconf.config.core import ConfigLoader

# --- Use tomllib (3.11+) with a fallback to tomli ---
try:
    import tomllib
except ImportError:
    # For Python < 3.11, use the 'tomli' package
    try:
        import tomli as tomllib
    except ImportError:
        logging.getLogger(__name__).error(
            "For Python < 3.11, the 'tomli' package is required for TOML parsing."
        )
        raise

logger = logging.getLogger(__name__)


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
