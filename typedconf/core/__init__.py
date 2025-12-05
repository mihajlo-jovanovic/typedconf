"""
typedconf.core - Core interfaces and implementations for language models.

Public API exports from core_interfaces.py and openai_model.py.
"""

# Export from core_interfaces.py
from typedconf.core.core_interfaces import (
    ChatMessage,
    ChatResponse,
    LanguageModel,
    MessageRole,
)

# Export from openai_model.py
from typedconf.core.openai_model import (
    OpenAILanguageModel,
)

__all__ = [
    # From core_interfaces.py
    "ChatMessage",
    "ChatResponse",
    "LanguageModel",
    "MessageRole",
    # From openai_model.py
    "OpenAILanguageModel",
]
