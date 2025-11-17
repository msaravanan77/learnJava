# Technical Specifications - Workspace Intelligence System

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
├────────────────────────────────────────────────────────────────┤
│  IDE Extensions (VSCode, IntelliJ, etc.)                       │
│  - LSP Client                                                   │
│  - WebSocket Client                                             │
│  - UI Components (Chat, Inline Suggestions)                    │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 │ HTTPS/WSS
                 │
┌────────────────▼───────────────────────────────────────────────┐
│                     API Gateway Layer                           │
├────────────────────────────────────────────────────────────────┤
│  - Authentication & Authorization                               │
│  - Rate Limiting                                                │
│  - Request Routing                                              │
│  - Load Balancing                                               │
└────────────────┬───────────────────────────────────────────────┘
                 │
        ┌────────┴────────┬────────────────┬──────────────┐
        │                 │                │              │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐  ┌───▼──────┐
│   Search     │  │   Context   │  │    LLM     │  │ Indexing │
│   Service    │  │   Engine    │  │  Service   │  │ Service  │
└───────┬──────┘  └──────┬──────┘  └─────┬──────┘  └───┬──────┘
        │                │                │              │
        └────────┬───────┴────────────────┴──────────────┘
                 │
┌────────────────▼───────────────────────────────────────────────┐
│                       Data Layer                                │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Qdrant      │  │  PostgreSQL  │  │    Redis     │         │
│  │ (Vectors)    │  │ (Metadata)   │  │   (Cache)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Models

### 2.1 Code Element Schema

```python
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class CodeElement(BaseModel):
    """Base model for all code elements"""
    id: str                          # UUID
    element_type: str                # function, class, method, variable
    name: str                        # Element name
    qualified_name: str              # Full qualified name
    file_path: str                   # Relative path from workspace root
    start_line: int
    end_line: int
    language: str                    # java, python, typescript, etc.
    content: str                     # Raw code content
    signature: Optional[str]         # Function/method signature
    docstring: Optional[str]         # Documentation
    comments: List[str]              # Inline comments
    embedding: List[float]           # 768-dimensional vector
    metadata: Dict[str, any]

class FunctionElement(CodeElement):
    """Function-specific fields"""
    parameters: List[Dict[str, str]]  # [{name, type, default}]
    return_type: Optional[str]
    complexity: int                   # Cyclomatic complexity
    calls: List[str]                  # Functions called
    called_by: List[str]              # Functions calling this

class ClassElement(CodeElement):
    """Class-specific fields"""
    methods: List[str]                # Method IDs
    attributes: List[Dict[str, str]]  # [{name, type, visibility}]
    inherits_from: List[str]          # Parent classes
    implements: List[str]             # Interfaces

class WorkspaceMetadata(BaseModel):
    """Workspace-level metadata"""
    workspace_id: str
    name: str
    root_path: str
    languages: List[str]
    total_files: int
    total_lines: int
    last_indexed: datetime
    indexing_status: str              # idle, indexing, error
```

### 2.2 Vector Database Schema (Qdrant)

```python
from qdrant_client.models import Distance, VectorParams

# Collection configuration
collection_config = {
    "vectors": VectorParams(
        size=768,                      # Embedding dimension
        distance=Distance.COSINE       # Similarity metric
    ),
    "shard_number": 4,                 # Number of shards
    "replication_factor": 2,           # Replication for HA
    "on_disk_payload": True            # Store payload on disk
}

# Point (Vector) structure
{
    "id": "uuid-string",
    "vector": [0.1, 0.2, ...],         # 768 dimensions
    "payload": {
        "workspace_id": "workspace-uuid",
        "file_path": "src/main/java/Example.java",
        "element_type": "function",
        "name": "processData",
        "qualified_name": "com.example.Service.processData",
        "language": "java",
        "signature": "public void processData(List<String> data)",
        "content": "public void processData...",
        "docstring": "Processes incoming data...",
        "start_line": 45,
        "end_line": 78,
        "complexity": 5,
        "dependencies": ["parseData", "validateInput"],
        "tags": ["data-processing", "core"],
        "last_modified": 1700000000,
        "author": "user@example.com"
    }
}
```

### 2.3 PostgreSQL Schema

```sql
-- Workspaces
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    root_path TEXT NOT NULL,
    repository_url TEXT,
    indexing_status VARCHAR(50) DEFAULT 'idle',
    last_indexed_at TIMESTAMP,
    total_files INTEGER DEFAULT 0,
    total_elements INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Files
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    language VARCHAR(50),
    file_hash VARCHAR(64),
    last_modified TIMESTAMP,
    indexed_at TIMESTAMP,
    element_count INTEGER DEFAULT 0,
    UNIQUE(workspace_id, file_path)
);

-- Code Elements (metadata only, vectors in Qdrant)
CREATE TABLE code_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    element_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    qualified_name TEXT,
    start_line INTEGER,
    end_line INTEGER,
    vector_id UUID,  -- Reference to Qdrant point ID
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dependencies
CREATE TABLE dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_element_id UUID REFERENCES code_elements(id) ON DELETE CASCADE,
    to_element_id UUID REFERENCES code_elements(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50), -- calls, imports, inherits, etc.
    UNIQUE(from_element_id, to_element_id, dependency_type)
);

-- Search Analytics
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id),
    query_text TEXT,
    query_type VARCHAR(50), -- semantic, keyword, hybrid
    results_count INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tenants (Multi-tenancy)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50), -- free, pro, enterprise
    api_key_hash VARCHAR(255),
    max_workspaces INTEGER DEFAULT 5,
    max_queries_per_day INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_files_workspace ON files(workspace_id);
CREATE INDEX idx_files_path ON files(file_path);
CREATE INDEX idx_elements_file ON code_elements(file_id);
CREATE INDEX idx_elements_name ON code_elements(name);
CREATE INDEX idx_dependencies_from ON dependencies(from_element_id);
CREATE INDEX idx_dependencies_to ON dependencies(to_element_id);
```

---

## 3. API Specifications

### 3.1 REST API Endpoints

#### Workspace Management

```
POST   /api/v1/workspaces
GET    /api/v1/workspaces
GET    /api/v1/workspaces/{id}
PUT    /api/v1/workspaces/{id}
DELETE /api/v1/workspaces/{id}
POST   /api/v1/workspaces/{id}/index
GET    /api/v1/workspaces/{id}/status
```

#### Search

```
POST   /api/v1/search/semantic
POST   /api/v1/search/keyword
POST   /api/v1/search/hybrid
GET    /api/v1/search/suggestions
```

**Request Example:**
```json
POST /api/v1/search/semantic
{
  "workspace_id": "uuid",
  "query": "function that handles user authentication",
  "filters": {
    "language": ["java", "kotlin"],
    "element_type": ["function", "method"],
    "file_pattern": "src/main/**"
  },
  "limit": 10,
  "include_context": true
}
```

**Response Example:**
```json
{
  "query_id": "uuid",
  "results": [
    {
      "id": "element-uuid",
      "score": 0.92,
      "element_type": "method",
      "name": "authenticateUser",
      "qualified_name": "com.example.auth.AuthService.authenticateUser",
      "file_path": "src/main/java/auth/AuthService.java",
      "start_line": 45,
      "end_line": 78,
      "signature": "public boolean authenticateUser(String username, String password)",
      "content": "...",
      "docstring": "Authenticates user credentials...",
      "context": {
        "dependencies": [...],
        "callers": [...]
      }
    }
  ],
  "total": 10,
  "latency_ms": 85
}
```

#### Context Engine

```
POST   /api/v1/context/completion
POST   /api/v1/context/chat
POST   /api/v1/context/explanation
```

**Request Example:**
```json
POST /api/v1/context/completion
{
  "workspace_id": "uuid",
  "file_path": "src/main/java/Service.java",
  "cursor_position": {
    "line": 45,
    "character": 12
  },
  "current_content": "...",
  "context_strategy": "smart" // smart, minimal, extensive
}
```

**Response Example:**
```json
{
  "context": {
    "current_file": {...},
    "relevant_code": [
      {
        "file_path": "...",
        "content": "...",
        "relevance_score": 0.88,
        "reason": "imports used in current file"
      }
    ],
    "dependencies": [...],
    "total_tokens": 2450
  }
}
```

#### LLM Integration

```
POST   /api/v1/llm/completion
POST   /api/v1/llm/chat
POST   /api/v1/llm/refactor
POST   /api/v1/llm/explain
```

### 3.2 WebSocket Protocol

**Connection:** `wss://api.example.com/ws?token={jwt_token}`

**Message Types:**

```typescript
// Client -> Server
interface ClientMessage {
  type: 'subscribe' | 'unsubscribe' | 'request';
  channel?: string;
  request_id?: string;
  data: any;
}

// Server -> Client
interface ServerMessage {
  type: 'update' | 'response' | 'error';
  channel?: string;
  request_id?: string;
  data: any;
}

// Real-time indexing updates
{
  "type": "update",
  "channel": "workspace:uuid:indexing",
  "data": {
    "status": "indexing",
    "progress": 45,
    "current_file": "src/main/Example.java"
  }
}

// Streaming LLM response
{
  "type": "response",
  "request_id": "uuid",
  "data": {
    "chunk": "public void process",
    "done": false
  }
}
```

### 3.3 Language Server Protocol (LSP)

**Supported Methods:**

```
# Lifecycle
initialize
initialized
shutdown
exit

# Document Synchronization
textDocument/didOpen
textDocument/didChange
textDocument/didSave
textDocument/didClose

# Language Features
textDocument/completion
textDocument/hover
textDocument/definition
textDocument/references
textDocument/documentSymbol
textDocument/codeAction
textDocument/formatting
```

**Completion Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "textDocument/completion",
  "params": {
    "textDocument": {
      "uri": "file:///workspace/src/Example.java"
    },
    "position": {
      "line": 45,
      "character": 12
    },
    "context": {
      "triggerKind": 1
    }
  }
}
```

**Completion Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "isIncomplete": false,
    "items": [
      {
        "label": "processData",
        "kind": 2,
        "detail": "AI-powered suggestion",
        "documentation": "Processes the data using...",
        "insertText": "processData(${1:data})",
        "insertTextFormat": 2,
        "data": {
          "source": "ai",
          "confidence": 0.92
        }
      }
    ]
  }
}
```

---

## 4. Embedding Strategy

### 4.1 Model Selection

**Primary Model:** `microsoft/graphcodebert-base`
- **Dimension:** 768
- **Max Tokens:** 512
- **Specialized for:** Code understanding with data flow

**Fallback Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension:** 384
- **Max Tokens:** 256
- **Specialized for:** General semantic similarity

### 4.2 Preprocessing Pipeline

```python
def preprocess_code_for_embedding(code_element: CodeElement) -> str:
    """Preprocess code element for optimal embedding"""

    components = []

    # 1. Add element type and name
    components.append(f"{code_element.element_type}: {code_element.name}")

    # 2. Add signature (for functions/methods)
    if code_element.signature:
        components.append(code_element.signature)

    # 3. Add docstring/comments (high weight)
    if code_element.docstring:
        components.append(code_element.docstring)

    # 4. Add normalized code content
    normalized_code = normalize_code(code_element.content)
    components.append(normalized_code)

    # 5. Add context (imports, dependencies)
    if code_element.metadata.get('imports'):
        components.append(f"imports: {', '.join(code_element.metadata['imports'])}")

    # Combine with separators
    text = " [SEP] ".join(components)

    # Truncate to max tokens
    return truncate_to_tokens(text, max_tokens=512)

def normalize_code(code: str) -> str:
    """Normalize code for better embedding"""
    # Remove excessive whitespace
    code = ' '.join(code.split())
    # Remove string literals (replace with placeholder)
    code = re.sub(r'"[^"]*"', '"STRING"', code)
    # Remove number literals
    code = re.sub(r'\b\d+\b', 'NUM', code)
    return code
```

### 4.3 Chunking Strategy

```python
class CodeChunker:
    """Smart code chunking for embedding"""

    def chunk_file(self, file_path: str, ast: AST) -> List[CodeElement]:
        """Chunk file based on AST"""
        chunks = []

        # Primary: Function/Method level
        for function in ast.functions:
            if self.is_chunkable(function):
                chunks.append(self.create_chunk(function, 'function'))

        # Secondary: Class level (with context)
        for class_def in ast.classes:
            chunks.append(self.create_class_chunk(class_def))

        # Tertiary: File level (for small files)
        if len(chunks) == 0 or self.is_small_file(file_path):
            chunks.append(self.create_file_chunk(file_path))

        return chunks

    def is_chunkable(self, function: FunctionNode) -> bool:
        """Determine if function should be chunked separately"""
        # Skip tiny functions (< 5 lines)
        if function.line_count < 5:
            return False
        # Skip auto-generated code
        if self.is_generated(function):
            return False
        return True
```

---

## 5. Search & Ranking

### 5.1 Hybrid Search Algorithm

```python
class HybridSearchEngine:
    def search(self, query: str, workspace_id: str, top_k: int = 10):
        # 1. Semantic search (vector similarity)
        semantic_results = self.semantic_search(query, workspace_id, top_k=20)

        # 2. Keyword search (BM25)
        keyword_results = self.keyword_search(query, workspace_id, top_k=20)

        # 3. Merge and re-rank
        merged = self.merge_results(semantic_results, keyword_results)

        # 4. Apply filters and boosting
        filtered = self.apply_filters(merged, self.filters)
        boosted = self.apply_boosting(filtered)

        # 5. Final re-ranking with cross-encoder
        final = self.rerank_with_cross_encoder(query, boosted, top_k=top_k)

        return final

    def merge_results(self, semantic, keyword):
        """Reciprocal Rank Fusion"""
        k = 60  # RRF constant
        scores = {}

        for rank, result in enumerate(semantic, 1):
            scores[result.id] = scores.get(result.id, 0) + 1 / (k + rank)

        for rank, result in enumerate(keyword, 1):
            scores[result.id] = scores.get(result.id, 0) + 1 / (k + rank)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### 5.2 Boosting Strategy

```python
def calculate_boost_score(element: CodeElement, context: SearchContext) -> float:
    """Calculate boosting multiplier"""
    boost = 1.0

    # Recency boost
    days_old = (datetime.now() - element.last_modified).days
    recency_boost = 1.0 / (1.0 + (days_old / 30))  # Decay over months
    boost *= (1 + recency_boost * 0.2)

    # Popularity boost (based on usage)
    if element.call_count > 10:
        boost *= 1.3

    # Same project boost
    if element.workspace_id == context.current_workspace_id:
        boost *= 1.5

    # Same language boost
    if element.language == context.current_language:
        boost *= 1.2

    # Has documentation boost
    if element.docstring and len(element.docstring) > 50:
        boost *= 1.1

    # Low complexity boost (easier to understand)
    if element.complexity < 10:
        boost *= 1.1

    return boost
```

---

## 6. Context Retrieval Strategy

### 6.1 Context Window Management

```python
class ContextBuilder:
    def build_context(self, cursor_position: Position, max_tokens: int = 4000):
        context_parts = []
        token_count = 0

        # Priority 1: Current file (around cursor)
        current_file_context = self.get_current_file_context(cursor_position)
        context_parts.append(current_file_context)
        token_count += self.count_tokens(current_file_context)

        # Priority 2: Imported/related files
        related_files = self.get_related_files(cursor_position.file)
        for file in related_files:
            if token_count > max_tokens:
                break
            file_context = self.get_file_summary(file)
            context_parts.append(file_context)
            token_count += self.count_tokens(file_context)

        # Priority 3: Semantically similar code
        similar_code = self.semantic_search(
            self.get_surrounding_code(cursor_position)
        )
        for code in similar_code[:5]:
            if token_count > max_tokens:
                break
            context_parts.append(code)
            token_count += self.count_tokens(code)

        # Priority 4: Project documentation
        if token_count < max_tokens * 0.8:
            docs = self.get_relevant_docs(cursor_position)
            context_parts.extend(docs)

        return self.format_context(context_parts)
```

### 6.2 Dependency Graph Traversal

```python
class DependencyGraph:
    def get_context_via_dependencies(self, element_id: str, max_depth: int = 3):
        """BFS traversal of dependency graph"""
        visited = set()
        queue = [(element_id, 0)]
        context = []

        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)
            element = self.get_element(current_id)
            context.append(element)

            # Add dependencies
            for dep in element.dependencies:
                if dep not in visited:
                    queue.append((dep, depth + 1))

        return context
```

---

## 7. Performance Optimizations

### 7.1 Caching Strategy

```python
# Multi-layer caching
class CacheManager:
    def __init__(self):
        self.l1_cache = LRUCache(maxsize=1000)     # In-memory
        self.l2_cache = RedisCache(ttl=3600)       # Redis
        self.l3_cache = None                       # CDN (for static)

    async def get_or_compute(self, key: str, compute_fn):
        # L1: In-memory
        if key in self.l1_cache:
            return self.l1_cache[key]

        # L2: Redis
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value
            return value

        # Compute
        value = await compute_fn()

        # Store in all layers
        self.l1_cache[key] = value
        await self.l2_cache.set(key, value)

        return value
```

### 7.2 Batch Processing

```python
class BatchEmbedder:
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        self.queue = asyncio.Queue()

    async def embed_with_batching(self, texts: List[str]):
        """Batch embedding requests for efficiency"""
        results = {}

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = await self.model.encode(batch)
            for text, emb in zip(batch, embeddings):
                results[text] = emb

        return results
```

### 7.3 Indexing Optimizations

```python
class IncrementalIndexer:
    def on_file_change(self, file_path: str):
        """Incremental indexing on file changes"""
        # 1. Parse only changed file
        ast = self.parser.parse(file_path)

        # 2. Find changed elements
        old_elements = self.db.get_elements_by_file(file_path)
        new_elements = self.extract_elements(ast)

        # 3. Compute diff
        to_delete = set(old_elements) - set(new_elements)
        to_add = set(new_elements) - set(old_elements)
        to_update = set(new_elements) & set(old_elements)

        # 4. Update vector DB (batch)
        self.vector_db.delete(to_delete)
        embeddings = self.embed_batch(to_add | to_update)
        self.vector_db.upsert(embeddings)

        # 5. Update dependency graph
        self.update_dependencies(file_path, new_elements)
```

---

## 8. Security Specifications

### 8.1 Authentication & Authorization

```python
# JWT Token Structure
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "workspace_ids": ["workspace-1", "workspace-2"],
  "role": "developer",
  "permissions": ["read:code", "write:code", "admin:workspace"],
  "iat": 1700000000,
  "exp": 1700003600
}

# RBAC Permissions
ROLES = {
    "viewer": ["read:code", "read:search"],
    "developer": ["read:code", "read:search", "write:code", "execute:llm"],
    "admin": ["*"]
}
```

### 8.2 Data Isolation

```python
# Row-Level Security (PostgreSQL)
CREATE POLICY workspace_isolation ON workspaces
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

# Vector DB Filtering
search_filter = {
    "must": [
        {"key": "tenant_id", "match": {"value": current_tenant_id}},
        {"key": "workspace_id", "match": {"any": user_workspace_ids}}
    ]
}
```

### 8.3 API Rate Limiting

```python
RATE_LIMITS = {
    "free": {
        "search": (100, "hour"),      # 100 per hour
        "llm": (20, "hour"),           # 20 per hour
        "embedding": (1000, "day")     # 1000 per day
    },
    "pro": {
        "search": (1000, "hour"),
        "llm": (200, "hour"),
        "embedding": (10000, "day")
    },
    "enterprise": {
        "search": (10000, "hour"),
        "llm": (2000, "hour"),
        "embedding": (100000, "day")
    }
}
```

---

## 9. Monitoring & Observability

### 9.1 Metrics

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Search metrics
search_latency = Histogram(
    'search_latency_seconds',
    'Search latency',
    ['search_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

embedding_generation_time = Histogram(
    'embedding_generation_seconds',
    'Embedding generation time'
)

# Business metrics
active_workspaces = Gauge(
    'active_workspaces',
    'Number of active workspaces'
)

indexed_elements = Counter(
    'indexed_elements_total',
    'Total indexed code elements',
    ['language']
)
```

### 9.2 Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("semantic_search")
async def semantic_search(query: str):
    span = trace.get_current_span()
    span.set_attribute("query.length", len(query))

    with tracer.start_as_current_span("embed_query"):
        embedding = await embed(query)

    with tracer.start_as_current_span("vector_search"):
        results = await vector_db.search(embedding)

    span.set_attribute("results.count", len(results))
    return results
```

---

## 10. Deployment Specifications

### 10.1 Kubernetes Resources

```yaml
# Resource Requirements
resources:
  search-service:
    requests:
      memory: "2Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"

  embedding-service:
    requests:
      memory: "4Gi"
      cpu: "2000m"
      nvidia.com/gpu: 1
    limits:
      memory: "8Gi"
      cpu: "4000m"
      nvidia.com/gpu: 1

  llm-service:
    requests:
      memory: "8Gi"
      cpu: "4000m"
      nvidia.com/gpu: 1
    limits:
      memory: "16Gi"
      cpu: "8000m"
      nvidia.com/gpu: 1
```

### 10.2 Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: search-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: search-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
