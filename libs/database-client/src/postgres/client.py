"""
PostgreSQL Database Client for Workspace Intelligence
"""

import asyncpg
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager


class PostgresClient:
    """Async PostgreSQL client for metadata and graph storage"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool"""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")

        async with self.pool.acquire() as connection:
            yield connection

    async def create_workspace(self, workspace_id: str, name: str, root_path: str) -> Dict:
        """Create a new workspace"""
        query = """
            INSERT INTO workspaces (id, name, root_path, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING id, name, root_path, created_at
        """
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, workspace_id, name, root_path)
            return dict(row)

    async def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace by ID"""
        query = "SELECT * FROM workspaces WHERE id = $1"
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, workspace_id)
            return dict(row) if row else None

    async def insert_code_element(
        self,
        element_id: str,
        workspace_id: str,
        file_path: str,
        name: str,
        element_type: str,
        language: str,
        start_line: int,
        end_line: int,
        code: str
    ) -> Dict:
        """Insert a code element"""
        query = """
            INSERT INTO code_elements (
                id, workspace_id, file_path, name, element_type,
                language, start_line, end_line, code, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
            RETURNING *
        """
        async with self.acquire() as conn:
            row = await conn.fetchrow(
                query, element_id, workspace_id, file_path, name,
                element_type, language, start_line, end_line, code
            )
            return dict(row)

    async def get_code_elements_by_file(self, workspace_id: str, file_path: str) -> List[Dict]:
        """Get all code elements in a file"""
        query = """
            SELECT * FROM code_elements
            WHERE workspace_id = $1 AND file_path = $2
            ORDER BY start_line
        """
        async with self.acquire() as conn:
            rows = await conn.fetch(query, workspace_id, file_path)
            return [dict(row) for row in rows]

    async def insert_file_dependency(
        self,
        workspace_id: str,
        source_file: str,
        target_file: str,
        import_type: str
    ) -> Dict:
        """Insert a file dependency relationship"""
        query = """
            INSERT INTO file_dependencies (workspace_id, source_file, target_file, import_type)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, workspace_id, source_file, target_file, import_type)
            return dict(row)

    async def get_file_dependencies(self, workspace_id: str, file_path: str) -> List[Dict]:
        """Get all dependencies for a file"""
        query = """
            SELECT * FROM file_dependencies
            WHERE workspace_id = $1 AND source_file = $2
        """
        async with self.acquire() as conn:
            rows = await conn.fetch(query, workspace_id, file_path)
            return [dict(row) for row in rows]

    async def get_dependency_graph(self, workspace_id: str, file_path: str, max_depth: int = 3) -> Dict:
        """
        Get dependency graph for a file using recursive CTE

        Returns a graph structure with nodes and edges
        """
        query = """
            WITH RECURSIVE dep_tree AS (
                -- Base case: direct dependencies
                SELECT source_file, target_file, import_type, 1 as depth
                FROM file_dependencies
                WHERE workspace_id = $1 AND source_file = $2

                UNION

                -- Recursive case: transitive dependencies
                SELECT fd.source_file, fd.target_file, fd.import_type, dt.depth + 1
                FROM file_dependencies fd
                INNER JOIN dep_tree dt ON fd.source_file = dt.target_file
                WHERE fd.workspace_id = $1 AND dt.depth < $3
            )
            SELECT DISTINCT source_file, target_file, import_type, depth
            FROM dep_tree
            ORDER BY depth, source_file, target_file
        """
        async with self.acquire() as conn:
            rows = await conn.fetch(query, workspace_id, file_path, max_depth)

            # Build graph structure
            nodes = set()
            edges = []

            for row in rows:
                nodes.add(row['source_file'])
                nodes.add(row['target_file'])
                edges.append({
                    'from': row['source_file'],
                    'to': row['target_file'],
                    'type': row['import_type'],
                    'depth': row['depth']
                })

            return {
                'root': file_path,
                'nodes': list(nodes),
                'edges': edges,
                'total_dependencies': len(edges)
            }

    async def search_code_elements(
        self,
        workspace_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """Full-text search for code elements"""
        search_query = """
            SELECT * FROM code_elements
            WHERE workspace_id = $1
            AND (
                name ILIKE $2
                OR code ILIKE $2
                OR docstring ILIKE $2
            )
            LIMIT $3
        """
        pattern = f"%{query}%"
        async with self.acquire() as conn:
            rows = await conn.fetch(search_query, workspace_id, pattern, limit)
            return [dict(row) for row in rows]


if __name__ == "__main__":
    import asyncio

    async def test():
        client = PostgresClient("postgresql://postgres:postgres@localhost:5432/workspace")
        await client.connect()

        # Test workspace creation
        workspace = await client.create_workspace(
            "ws123",
            "My Workspace",
            "/home/user/projects/myapp"
        )
        print(f"Created workspace: {workspace}")

        await client.close()

    asyncio.run(test())
