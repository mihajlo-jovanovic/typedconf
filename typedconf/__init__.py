"""
typedconf - A simple, opinionated configuration manager for Python applications.

This package provides:
- Configuration management with TOML files and environment variables
- Language model interfaces and implementations
"""

# Re-export config public API
from typedconf.config import (
    AppConfig,
    Config,
    ConfigDict,
    ConfigModel,
    Field,
    LanguageModelConfig,
    ValidationError,
)

# Re-export core public API
from typedconf.core import (
    ChatMessage,
    ChatResponse,
    LanguageModel,
    MessageRole,
    OpenAILanguageModel,
)

__version__ = "0.1.0"

__all__ = [
    # Configuration
    "AppConfig",
    "Config",
    "ConfigDict",
    "ConfigModel",
    "Field",
    "LanguageModelConfig",
    "ValidationError",
    # Core
    "ChatMessage",
    "ChatResponse",
    "LanguageModel",
    "MessageRole",
    "OpenAILanguageModel",
]
