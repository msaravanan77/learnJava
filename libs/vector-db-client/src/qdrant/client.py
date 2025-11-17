"""
Qdrant vector database client for workspace intelligence
"""

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, SearchParams
)
import uuid


class WorkspaceVectorDB:
    """Qdrant client for workspace intelligence"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "code_elements"
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,  # GraphCodeBERT dimension
                    distance=Distance.COSINE
                ),
                shard_number=4,
                replication_factor=2,
                on_disk_payload=True
            )
            print(f"Created collection: {self.collection_name}")

    def upsert_code_element(
        self,
        embedding: List[float],
        metadata: Dict,
        element_id: Optional[str] = None
    ) -> str:
        """Insert or update a code element"""
        if element_id is None:
            element_id = str(uuid.uuid4())

        point = PointStruct(
            id=element_id,
            vector=embedding,
            payload=metadata
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return element_id

    def upsert_batch(
        self,
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Batch insert/update code elements"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in embeddings]

        points = [
            PointStruct(id=id_, vector=emb, payload=meta)
            for id_, emb, meta in zip(ids, embeddings, metadatas)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

        return ids

    def search(
        self,
        query_embedding: List[float],
        workspace_id: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Semantic search for code elements"""
        # Build filter
        must_conditions = [
            FieldCondition(
                key="workspace_id",
                match=MatchValue(value=workspace_id)
            )
        ]

        if filters:
            if language := filters.get('language'):
                must_conditions.append(
                    FieldCondition(
                        key="language",
                        match=MatchValue(value=language)
                    )
                )
            if element_type := filters.get('element_type'):
                must_conditions.append(
                    FieldCondition(
                        key="element_type",
                        match=MatchValue(value=element_type)
                    )
                )

        search_filter = Filter(must=must_conditions) if must_conditions else None

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False
            )
        )

        # Format results
        formatted = []
        for result in results:
            formatted.append({
                'id': result.id,
                'score': result.score,
                **result.payload
            })

        return formatted

    def delete_by_workspace(self, workspace_id: str):
        """Delete all elements for a workspace"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="workspace_id",
                        match=MatchValue(value=workspace_id)
                    )
                ]
            )
        )


if __name__ == "__main__":
    # Example usage
    db = WorkspaceVectorDB()

    # Sample embeddings
    import numpy as np
    embeddings = [
        np.random.rand(768).tolist(),
        np.random.rand(768).tolist(),
    ]

    metadatas = [
        {
            'workspace_id': 'workspace-123',
            'file_path': 'src/auth/AuthService.java',
            'element_type': 'method',
            'name': 'authenticateUser',
            'language': 'java',
            'signature': 'public boolean authenticateUser(String username, String password)',
            'content': '...',
            'start_line': 45,
            'end_line': 78
        },
        {
            'workspace_id': 'workspace-123',
            'file_path': 'src/utils/Validator.java',
            'element_type': 'method',
            'name': 'validateEmail',
            'language': 'java',
            'signature': 'private boolean validateEmail(String email)',
            'content': '...',
            'start_line': 12,
            'end_line': 20
        }
    ]

    # Insert
    ids = db.upsert_batch(embeddings, metadatas)
    print(f"Inserted {len(ids)} elements")

    # Search
    query_embedding = np.random.rand(768).tolist()
    results = db.search(
        query_embedding=query_embedding,
        workspace_id='workspace-123',
        limit=5,
        filters={'language': 'java'}
    )

    print(f"\nSearch results:")
    for result in results:
        print(f"  - {result['name']} (score: {result['score']:.4f})")
