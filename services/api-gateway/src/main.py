"""
API Gateway Service - Central entry point for all API requests
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import httpx
import os
import uvicorn

from middleware.auth import AuthMiddleware, RateLimiter, security


app = FastAPI(title="API Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth and rate limiting
auth_middleware = AuthMiddleware(secret_key=os.getenv("JWT_SECRET", "your-secret-key"))
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

# Service URLs
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8001")
CONTEXT_SERVICE_URL = os.getenv("CONTEXT_SERVICE_URL", "http://context-engine:8003")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8004")
INDEXING_SERVICE_URL = os.getenv("INDEXING_SERVICE_URL", "http://indexing-service:8000")


async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify authentication and rate limiting"""
    payload = await auth_middleware.authenticate(credentials)
    await rate_limiter.check_rate_limit(payload["user_id"])
    return payload


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/api/v1/status")
async def get_status(user: dict = Depends(verify_auth)):
    """Get system status"""
    services = {
        "search": SEARCH_SERVICE_URL,
        "context": CONTEXT_SERVICE_URL,
        "llm": LLM_SERVICE_URL,
        "indexing": INDEXING_SERVICE_URL
    }

    status_results = {}
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health", timeout=2.0)
                status_results[name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                status_results[name] = "unavailable"

    return {
        "gateway": "healthy",
        "services": status_results,
        "user_id": user["user_id"],
        "workspace_id": user["workspace_id"]
    }


@app.post("/api/v1/search")
async def search_code(request: Request, user: dict = Depends(verify_auth)):
    """Proxy to search service"""
    body = await request.json()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SEARCH_SERVICE_URL}/api/v1/search",
                json=body,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Search service error: {str(e)}")


@app.post("/api/v1/completion")
async def generate_completion(request: Request, user: dict = Depends(verify_auth)):
    """
    Generate code completion

    Flow: Request → Context Engine → LLM Service → Response
    """
    body = await request.json()

    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Build context
            context_response = await client.post(
                f"{CONTEXT_SERVICE_URL}/api/v1/context",
                json={
                    "file_path": body.get("file_path"),
                    "cursor_line": body.get("cursor_line"),
                    "cursor_column": body.get("cursor_column"),
                    "query": body.get("query", "")
                },
                timeout=10.0
            )
            context_response.raise_for_status()
            context_data = context_response.json()

            # Step 2: Generate completion
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/api/v1/completion",
                json={
                    "prompt": body.get("query", "Complete the code"),
                    "context": str(context_data["relevant_snippets"]),
                    "max_tokens": body.get("max_tokens", 2000),
                    "temperature": body.get("temperature", 0.7),
                    "stream": False
                },
                timeout=30.0
            )
            llm_response.raise_for_status()

            return llm_response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Completion error: {str(e)}")


@app.post("/api/v1/chat")
async def chat_with_codebase(request: Request, user: dict = Depends(verify_auth)):
    """Chat about codebase"""
    body = await request.json()

    async with httpx.AsyncClient() as client:
        try:
            # Build context from search
            search_response = await client.post(
                f"{SEARCH_SERVICE_URL}/api/v1/search",
                json={"query": body.get("question"), "top_k": 5},
                timeout=10.0
            )
            search_response.raise_for_status()
            search_results = search_response.json()

            # Generate answer
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/api/v1/chat",
                json={
                    "prompt": body.get("question"),
                    "context": str(search_results),
                    "max_tokens": body.get("max_tokens", 1000),
                    "temperature": 0.7
                },
                timeout=30.0
            )
            llm_response.raise_for_status()

            return llm_response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/v1/index/workspace")
async def index_workspace(request: Request, user: dict = Depends(verify_auth)):
    """Trigger workspace indexing"""
    body = await request.json()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INDEXING_SERVICE_URL}/api/v1/index/workspace",
                json=body,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")


@app.post("/api/v1/auth/token")
async def create_auth_token(user_id: str, workspace_id: str):
    """Create authentication token (for testing/development)"""
    token = auth_middleware.create_token(user_id, workspace_id)
    return {"token": token, "type": "bearer"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
