from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    
@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    response_time: Optional[float] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class LanguageModel(ABC):
    @abstractmethod
    def invoke(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        pass
