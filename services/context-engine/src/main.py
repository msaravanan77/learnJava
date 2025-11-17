"""
Context Engine Service - FastAPI application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from engine.context_builder import ContextBuilder


app = FastAPI(title="Context Engine Service", version="1.0.0")

# Initialize context builder
context_builder = ContextBuilder(
    search_service_url="http://search-service:8001",
    db_connection_string="postgresql://postgres:postgres@postgres:5432/workspace"
)


class ContextRequest(BaseModel):
    file_path: str
    cursor_line: int
    cursor_column: int
    query: str
    max_tokens: Optional[int] = 3500


class ContextResponse(BaseModel):
    current_file: str
    cursor_position: Dict[str, int]
    relevant_snippets: List[Dict[str, Any]]
    dependencies: List[str]
    total_tokens: int


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "context-engine"}


@app.post("/api/v1/context", response_model=ContextResponse)
async def build_context(request: ContextRequest):
    """
    Build context for code completion or chat request

    Args:
        request: Context request with file info and query

    Returns:
        ContextResponse with relevant code snippets
    """
    try:
        context = await context_builder.build_context(
            file_path=request.file_path,
            cursor_line=request.cursor_line,
            cursor_column=request.cursor_column,
            query=request.query
        )

        return ContextResponse(
            current_file=context.current_file,
            cursor_position=context.cursor_position,
            relevant_snippets=context.relevant_snippets,
            dependencies=context.dependencies,
            total_tokens=context.total_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context building failed: {str(e)}")


@app.get("/api/v1/dependencies/{file_path:path}")
async def get_dependencies(file_path: str):
    """
    Get dependencies for a specific file

    Args:
        file_path: File path to get dependencies for

    Returns:
        List of dependency file paths
    """
    try:
        dependencies = await context_builder._get_dependencies(file_path)
        return {"file": file_path, "dependencies": dependencies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dependencies: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
