"""
LLM Service - FastAPI application for AI model integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os
import uvicorn

from providers.llm_provider import LLMProviderFactory, LLMRequest


app = FastAPI(title="LLM Service", version="1.0.0")

# Initialize LLM provider from environment
provider_name = os.getenv("LLM_PROVIDER", "openai")
api_key = os.getenv("LLM_API_KEY", "")
model = os.getenv("LLM_MODEL")

llm_provider = None
if api_key:
    llm_provider = LLMProviderFactory.create(provider_name, api_key, model)


class CompletionRequest(BaseModel):
    prompt: str
    context: str
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


class CompletionResponse(BaseModel):
    text: str
    model: str
    tokens_used: int
    finish_reason: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llm-service",
        "provider": provider_name,
        "model": model or "default"
    }


@app.post("/api/v1/completion", response_model=CompletionResponse)
async def generate_completion(request: CompletionRequest):
    """
    Generate code completion using LLM

    Args:
        request: Completion request with prompt and context

    Returns:
        CompletionResponse with generated text
    """
    if not llm_provider:
        raise HTTPException(status_code=503, detail="LLM provider not configured")

    try:
        llm_request = LLMRequest(
            prompt=request.prompt,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False
        )

        response = await llm_provider.generate(llm_request)

        return CompletionResponse(
            text=response.text,
            model=response.model,
            tokens_used=response.tokens_used,
            finish_reason=response.finish_reason
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completion failed: {str(e)}")


@app.post("/api/v1/completion/stream")
async def generate_completion_stream(request: CompletionRequest):
    """
    Generate streaming code completion using LLM

    Args:
        request: Completion request with prompt and context

    Returns:
        StreamingResponse with generated text chunks
    """
    if not llm_provider:
        raise HTTPException(status_code=503, detail="LLM provider not configured")

    try:
        llm_request = LLMRequest(
            prompt=request.prompt,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )

        async def event_generator():
            try:
                async for chunk in llm_provider.generate_stream(llm_request):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming completion failed: {str(e)}")


@app.post("/api/v1/chat")
async def chat_with_codebase(request: CompletionRequest):
    """
    Chat about codebase using LLM

    Args:
        request: Chat request with question and context

    Returns:
        CompletionResponse with answer
    """
    # Same as completion but with chat-optimized prompt
    return await generate_completion(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
