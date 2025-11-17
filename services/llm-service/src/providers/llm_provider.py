"""
LLM Provider Abstraction - Support for multiple AI providers
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
from dataclasses import dataclass
import httpx
import json


@dataclass
class LLMRequest:
    """Request to LLM provider"""
    prompt: str
    context: str
    max_tokens: int = 2000
    temperature: float = 0.7
    stream: bool = False


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    text: str
    model: str
    tokens_used: int
    finish_reason: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion (non-streaming)"""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate completion (streaming)"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": request.context},
                        {"role": "user", "content": request.prompt}
                    ],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                text=data["choices"][0]["message"]["content"],
                model=data["model"],
                tokens_used=data["usage"]["total_tokens"],
                finish_reason=data["choices"][0]["finish_reason"]
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate streaming completion using OpenAI API"""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": request.context},
                        {"role": "user", "content": request.prompt}
                    ],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "stream": True
                },
                timeout=60.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion using Anthropic API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": request.max_tokens,
                    "messages": [
                        {"role": "user", "content": f"{request.context}\n\n{request.prompt}"}
                    ],
                    "temperature": request.temperature,
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                text=data["content"][0]["text"],
                model=data["model"],
                tokens_used=data["usage"]["input_tokens"] + data["usage"]["output_tokens"],
                finish_reason=data["stop_reason"]
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate streaming completion using Anthropic API"""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": request.max_tokens,
                    "messages": [
                        {"role": "user", "content": f"{request.context}\n\n{request.prompt}"}
                    ],
                    "temperature": request.temperature,
                    "stream": True
                },
                timeout=60.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            chunk = json.loads(data)
                            if chunk.get("type") == "content_block_delta":
                                delta = chunk.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                        except json.JSONDecodeError:
                            continue


class LLMProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create(provider_name: str, api_key: str, model: Optional[str] = None) -> LLMProvider:
        """
        Create an LLM provider instance

        Args:
            provider_name: Name of provider ('openai', 'anthropic')
            api_key: API key for the provider
            model: Optional model name

        Returns:
            LLMProvider instance
        """
        providers = {
            "openai": lambda: OpenAIProvider(api_key, model or "gpt-4"),
            "anthropic": lambda: AnthropicProvider(api_key, model or "claude-3-opus-20240229"),
        }

        if provider_name.lower() not in providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        return providers[provider_name.lower()]()
