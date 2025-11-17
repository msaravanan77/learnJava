"""
Context Engine - Builds relevant context for LLM prompts
"""

from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass


@dataclass
class CodeContext:
    """Represents code context for a request"""
    current_file: str
    cursor_position: Dict[str, int]
    relevant_snippets: List[Dict[str, Any]]
    dependencies: List[str]
    total_tokens: int


class ContextBuilder:
    """Builds optimized context for LLM requests"""

    def __init__(self, search_service_url: str, db_connection_string: str, max_tokens: int = 3500):
        self.search_service_url = search_service_url
        self.db_connection_string = db_connection_string
        self.max_tokens = max_tokens

    async def build_context(
        self,
        file_path: str,
        cursor_line: int,
        cursor_column: int,
        query: str
    ) -> CodeContext:
        """
        Build comprehensive context for code completion/chat

        Args:
            file_path: Current file path
            cursor_line: Cursor line number
            cursor_column: Cursor column number
            query: User query or completion request

        Returns:
            CodeContext with relevant code snippets and dependencies
        """
        # Gather context from multiple sources concurrently
        current_file_context = await self._get_current_file_context(file_path, cursor_line)
        similar_snippets = await self._search_similar_code(query)
        dependencies = await self._get_dependencies(file_path)

        # Optimize context to fit within token limit
        optimized_snippets = self._optimize_snippets(
            current_file_context,
            similar_snippets,
            dependencies
        )

        return CodeContext(
            current_file=file_path,
            cursor_position={"line": cursor_line, "column": cursor_column},
            relevant_snippets=optimized_snippets,
            dependencies=dependencies,
            total_tokens=self._count_tokens(optimized_snippets)
        )

    async def _get_current_file_context(self, file_path: str, cursor_line: int) -> Dict:
        """Extract context from current file around cursor"""
        # In production, read actual file and extract relevant lines
        context_window = 50  # lines before and after cursor
        return {
            "file_path": file_path,
            "start_line": max(0, cursor_line - context_window),
            "end_line": cursor_line + context_window,
            "content": "# Current file content would be here"
        }

    async def _search_similar_code(self, query: str) -> List[Dict]:
        """Search for similar code using semantic search"""
        # Call search service API
        # In production, make HTTP request to search service
        return [
            {
                "file": "example.py",
                "function": "similar_function",
                "code": "def similar_function(): pass",
                "similarity": 0.85
            }
        ]

    async def _get_dependencies(self, file_path: str) -> List[str]:
        """Get file dependencies from database"""
        # Query PostgreSQL for dependency graph
        return ["dependency1.py", "dependency2.py"]

    def _optimize_snippets(
        self,
        current_context: Dict,
        snippets: List[Dict],
        dependencies: List[str]
    ) -> List[Dict]:
        """Optimize snippets to fit within token budget"""
        optimized = []
        token_count = 0

        # Always include current file context first
        current_tokens = self._count_tokens([current_context])
        if token_count + current_tokens < self.max_tokens:
            optimized.append(current_context)
            token_count += current_tokens

        # Add snippets by relevance until we hit token limit
        for snippet in sorted(snippets, key=lambda x: x.get('similarity', 0), reverse=True):
            snippet_tokens = self._estimate_tokens(snippet.get('code', ''))
            if token_count + snippet_tokens < self.max_tokens:
                optimized.append(snippet)
                token_count += snippet_tokens
            else:
                break

        return optimized

    def _count_tokens(self, snippets: List[Dict]) -> int:
        """Count total tokens in snippets"""
        total = 0
        for snippet in snippets:
            content = snippet.get('content', '') or snippet.get('code', '')
            total += self._estimate_tokens(content)
        return total

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 chars)"""
        return len(text) // 4


if __name__ == "__main__":
    # Example usage
    builder = ContextBuilder(
        search_service_url="http://localhost:8001",
        db_connection_string="postgresql://localhost/workspace"
    )

    # Test context building
    async def test():
        context = await builder.build_context(
            file_path="src/main.py",
            cursor_line=42,
            cursor_column=10,
            query="implement user authentication"
        )
        print(f"Built context for {context.current_file}")
        print(f"Total tokens: {context.total_tokens}")
        print(f"Snippets: {len(context.relevant_snippets)}")
        print(f"Dependencies: {context.dependencies}")

    asyncio.run(test())
