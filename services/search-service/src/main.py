"""
Search Service - Semantic search for code elements
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import time

app = FastAPI(title="Search Service", version="1.0.0")


# Models
class SearchRequest(BaseModel):
    workspace_id: str
    query: str
    filters: Optional[Dict] = None
    limit: int = 10
    search_type: str = "semantic"  # semantic, keyword, hybrid


class SearchResult(BaseModel):
    id: str
    score: float
    element_type: str
    name: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    signature: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    latency_ms: int


# Service
class SearchService:
    def __init__(self, vector_db, embedding_service):
        self.vector_db = vector_db
        self.embedder = embedding_service

    async def search(self, request: SearchRequest) -> SearchResponse:
        start = time.time()

        # Generate query embedding
        query_embedding = await self.embedder.embed_single(request.query)

        # Search vector DB
        results = await self.vector_db.search(
            query_embedding=query_embedding,
            workspace_id=request.workspace_id,
            limit=request.limit,
            filters=request.filters
        )

        latency_ms = int((time.time() - start) * 1000)

        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            total=len(results),
            latency_ms=latency_ms
        )


# Routes
@app.post("/api/v1/search/semantic", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Semantic search endpoint"""
    try:
        service = get_search_service()
        return await service.search(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "search-service"}


# Dependency injection
def get_search_service():
    # This will be properly initialized in production
    # For now, return a placeholder
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
