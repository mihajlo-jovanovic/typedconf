import time
from typing import Any, Dict, List, Optional

import openai
from openai.types.chat import ChatCompletion

from typedconf.config.user_config import ModelConfig
from typedconf.core.core_interfaces import (
    ChatMessage,
    ChatResponse,
    LanguageModel,
    MessageRole,
)


class OpenAILanguageModel(LanguageModel):
    def __init__(self, model_config: ModelConfig, api_key: Optional[str] = None):
        self.client = openai.Client(api_key=api_key)
        self.model_config = model_config

    def invoke(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        openai_messages = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

        # Merge model config with any additional kwargs
        api_params = {
            "model": self.model_config.id,
            "temperature": self.model_config.temperature,
            "max_tokens": self.model_config.max_tokens,
            "top_p": self.model_config.top_p,
            **kwargs,  # Allow overrides via kwargs
        }

        start_time = time.time()
        response: ChatCompletion = self.client.chat.completions.create(
            messages=openai_messages,
            **api_params,
        )
        end_time = time.time()

        choice = response.choices[0]
        
        return ChatResponse(
            content=choice.message.content or "",
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
            response_time=end_time - start_time,
            finish_reason=choice.finish_reason,
            metadata={"system_fingerprint": response.system_fingerprint},
        )
