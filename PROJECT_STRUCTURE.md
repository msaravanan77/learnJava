# Project Structure - Workspace Intelligence System

## Repository Organization

### Monorepo Structure (Recommended for Enterprise)

```
workspace-intelligence/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy-staging.yml
│   │   ├── deploy-production.yml
│   │   └── security-scan.yml
│   └── CODEOWNERS
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   └── user-guides/
│
├── services/
│   ├── api-gateway/
│   ├── search-service/
│   ├── context-engine/
│   ├── llm-service/
│   ├── indexing-service/
│   └── embedding-service/
│
├── ide-extensions/
│   ├── vscode/
│   ├── intellij/
│   └── lsp-server/
│
├── libs/
│   ├── shared-types/
│   ├── database-client/
│   ├── vector-db-client/
│   └── common-utils/
│
├── infrastructure/
│   ├── kubernetes/
│   ├── terraform/
│   ├── docker/
│   └── monitoring/
│
├── scripts/
│   ├── setup/
│   ├── migration/
│   └── deployment/
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── performance/
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
├── README.md
└── .gitignore
```

---

## Detailed Service Structure

### 1. API Gateway

```
services/api-gateway/
├── src/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   └── logging.py
│   ├── middleware/
│   │   ├── auth.py
│   │   ├── rate_limit.py
│   │   ├── cors.py
│   │   └── request_id.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── workspaces.py
│   │   ├── search.py
│   │   ├── context.py
│   │   └── llm.py
│   └── utils/
│       ├── jwt.py
│       └── http_client.py
├── tests/
│   ├── test_auth.py
│   └── test_routes.py
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
redis==5.0.1
httpx==0.25.2
prometheus-client==0.19.0
opentelemetry-api==1.21.0
```

---

### 2. Indexing Service

```
services/indexing-service/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── tree_sitter_manager.py
│   │   └── language_parsers/
│   │       ├── java_parser.py
│   │       ├── python_parser.py
│   │       ├── typescript_parser.py
│   │       ├── javascript_parser.py
│   │       ├── go_parser.py
│   │       └── rust_parser.py
│   ├── extractors/
│   │   ├── function_extractor.py
│   │   ├── class_extractor.py
│   │   ├── import_extractor.py
│   │   └── comment_extractor.py
│   ├── models/
│   │   ├── code_element.py
│   │   ├── workspace.py
│   │   └── file_metadata.py
│   ├── indexer/
│   │   ├── workspace_indexer.py
│   │   ├── incremental_indexer.py
│   │   ├── file_watcher.py
│   │   └── dependency_graph.py
│   ├── database/
│   │   ├── postgres_client.py
│   │   └── vector_db_client.py
│   └── workers/
│       ├── index_worker.py
│       └── task_queue.py
├── tests/
│   ├── test_parsers/
│   ├── test_extractors/
│   └── test_indexer/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
tree-sitter==0.20.4
tree-sitter-languages==1.9.1
watchdog==3.0.0
gitignore-parser==0.1.9
asyncpg==0.29.0
celery==5.3.4
redis==5.0.1
qdrant-client==1.7.0
```

---

### 3. Embedding Service

```
services/embedding-service/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── model_manager.py
│   │   ├── sentence_transformer.py
│   │   ├── code_bert.py
│   │   └── model_registry.py
│   ├── preprocessing/
│   │   ├── code_normalizer.py
│   │   ├── tokenizer.py
│   │   └── chunker.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── batch/
│   │   ├── batch_processor.py
│   │   └── queue_manager.py
│   └── cache/
│       └── embedding_cache.py
├── models/  # Model weights
│   └── .gitkeep
├── tests/
│   ├── test_models/
│   └── test_preprocessing/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
torch==2.1.2
transformers==4.36.2
sentence-transformers==2.2.2
accelerate==0.25.0
einops==0.7.0
fastapi==0.104.1
redis==5.0.1
```

---

### 4. Search Service

```
services/search-service/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── search/
│   │   ├── semantic_search.py
│   │   ├── keyword_search.py
│   │   ├── hybrid_search.py
│   │   └── filters.py
│   ├── ranking/
│   │   ├── reranker.py
│   │   ├── cross_encoder.py
│   │   └── boosting.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── database/
│   │   ├── vector_db.py
│   │   ├── postgres.py
│   │   └── elasticsearch.py
│   └── cache/
│       └── query_cache.py
├── tests/
│   ├── test_search/
│   └── test_ranking/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
qdrant-client==1.7.0
elasticsearch==8.11.1
numpy==1.26.2
scikit-learn==1.3.2
fastapi==0.104.1
redis==5.0.1
sentence-transformers==2.2.2  # For cross-encoder
```

---

### 5. Context Engine

```
services/context-engine/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── retrieval/
│   │   ├── context_retriever.py
│   │   ├── graph_traversal.py
│   │   ├── relevance_scorer.py
│   │   └── deduplication.py
│   ├── strategies/
│   │   ├── completion_context.py
│   │   ├── chat_context.py
│   │   ├── refactor_context.py
│   │   └── debug_context.py
│   ├── compression/
│   │   ├── token_optimizer.py
│   │   └── context_compressor.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   └── graph/
│       ├── dependency_graph.py
│       └── call_graph.py
├── tests/
│   ├── test_retrieval/
│   └── test_strategies/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
networkx==3.2.1
fastapi==0.104.1
asyncpg==0.29.0
redis==5.0.1
tiktoken==0.5.2  # Token counting
```

---

### 6. LLM Service

```
services/llm-service/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── providers/
│   │   ├── base_provider.py
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── azure_provider.py
│   │   └── local_model_provider.py
│   ├── prompts/
│   │   ├── prompt_manager.py
│   │   ├── templates/
│   │   │   ├── completion.txt
│   │   │   ├── chat.txt
│   │   │   ├── refactor.txt
│   │   │   └── explain.txt
│   │   └── prompt_builder.py
│   ├── streaming/
│   │   ├── response_streamer.py
│   │   └── websocket_handler.py
│   ├── rate_limiting/
│   │   ├── token_bucket.py
│   │   └── cost_tracker.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   └── cache/
│       └── response_cache.py
├── tests/
│   ├── test_providers/
│   └── test_prompts/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
openai==1.6.1
anthropic==0.8.1
vllm==0.2.6  # For local models
fastapi==0.104.1
websockets==12.0
redis==5.0.1
tenacity==8.2.3  # Retry logic
```

---

### 7. LSP Server

```
ide-extensions/lsp-server/
├── src/
│   ├── server.py
│   ├── config.py
│   ├── handlers/
│   │   ├── completion.py
│   │   ├── hover.py
│   │   ├── definition.py
│   │   ├── references.py
│   │   ├── document_symbol.py
│   │   └── code_action.py
│   ├── managers/
│   │   ├── workspace_manager.py
│   │   ├── document_manager.py
│   │   └── cache_manager.py
│   ├── client/
│   │   ├── api_client.py
│   │   └── websocket_client.py
│   └── utils/
│       ├── lsp_types.py
│       └── position_utils.py
├── tests/
│   ├── test_handlers/
│   └── test_managers/
├── requirements.txt
├── Dockerfile
└── README.md
```

**Key Dependencies:**
```txt
pygls==1.2.1  # Language Server Protocol
lsprotocol==2023.0.0
httpx==0.25.2
websockets==12.0
```

---

### 8. VSCode Extension

```
ide-extensions/vscode/
├── src/
│   ├── extension.ts
│   ├── client/
│   │   ├── lspClient.ts
│   │   └── websocketClient.ts
│   ├── providers/
│   │   ├── completionProvider.ts
│   │   ├── hoverProvider.ts
│   │   └── inlineCompletionProvider.ts
│   ├── ui/
│   │   ├── chatPanel.ts
│   │   ├── statusBar.ts
│   │   └── webview/
│   │       ├── chat.html
│   │       ├── chat.css
│   │       └── chat.js
│   ├── commands/
│   │   ├── explainCode.ts
│   │   ├── refactor.ts
│   │   ├── generateTests.ts
│   │   └── indexWorkspace.ts
│   ├── settings/
│   │   └── configuration.ts
│   ├── telemetry/
│   │   └── analytics.ts
│   └── utils/
│       ├── logger.ts
│       └── tokenizer.ts
├── resources/
│   ├── icons/
│   └── snippets/
├── test/
│   ├── suite/
│   └── runTest.ts
├── package.json
├── tsconfig.json
├── webpack.config.js
├── .vscodeignore
└── README.md
```

**package.json:**
```json
{
  "name": "workspace-intelligence",
  "displayName": "Workspace Intelligence",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Programming Languages", "Machine Learning"],
  "activationEvents": ["onStartupFinished"],
  "main": "./dist/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "workspaceIntelligence.explainCode",
        "title": "Explain Code"
      },
      {
        "command": "workspaceIntelligence.refactor",
        "title": "Refactor Code"
      }
    ],
    "configuration": {
      "title": "Workspace Intelligence",
      "properties": {
        "workspaceIntelligence.apiEndpoint": {
          "type": "string",
          "default": "http://localhost:8080"
        }
      }
    }
  },
  "dependencies": {
    "vscode-languageclient": "^9.0.1",
    "ws": "^8.14.2",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.10.5",
    "typescript": "^5.3.3",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4",
    "ts-loader": "^9.5.1"
  }
}
```

---

### 9. IntelliJ Plugin

```
ide-extensions/intellij/
├── src/main/
│   ├── kotlin/
│   │   └── com/workspaceintel/plugin/
│   │       ├── Plugin.kt
│   │       ├── services/
│   │       │   ├── LSPService.kt
│   │       │   ├── IndexingService.kt
│   │       │   └── ApiService.kt
│   │       ├── actions/
│   │       │   ├── ExplainCodeAction.kt
│   │       │   ├── RefactorAction.kt
│   │       │   └── GenerateTestAction.kt
│   │       ├── ui/
│   │       │   ├── ChatToolWindow.kt
│   │       │   ├── SettingsDialog.kt
│   │       │   └── InlayProvider.kt
│   │       ├── completion/
│   │       │   └── CompletionContributor.kt
│   │       └── utils/
│   │           ├── Logger.kt
│   │           └── HttpClient.kt
│   └── resources/
│       ├── META-INF/
│       │   └── plugin.xml
│       └── icons/
├── src/test/
│   └── kotlin/
├── build.gradle.kts
└── README.md
```

**build.gradle.kts:**
```kotlin
plugins {
    id("org.jetbrains.kotlin.jvm") version "1.9.21"
    id("org.jetbrains.intellij") version "1.16.1"
}

intellij {
    version.set("2023.3")
    type.set("IC")
    plugins.set(listOf("com.intellij.java"))
}

dependencies {
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-cio:2.3.7")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
}
```

---

### 10. Shared Libraries

```
libs/shared-types/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── code_element.py
│   │   ├── workspace.py
│   │   ├── search.py
│   │   └── context.py
│   └── enums/
│       ├── language.py
│       └── element_type.py
├── tests/
├── setup.py
└── README.md

libs/database-client/
├── src/
│   ├── __init__.py
│   ├── postgres/
│   │   ├── client.py
│   │   ├── models.py
│   │   └── migrations/
│   └── redis/
│       └── client.py
├── tests/
├── setup.py
└── README.md

libs/vector-db-client/
├── src/
│   ├── __init__.py
│   ├── qdrant/
│   │   ├── client.py
│   │   ├── collections.py
│   │   └── schemas.py
│   └── base/
│       └── interface.py
├── tests/
├── setup.py
└── README.md
```

---

## Infrastructure Structure

### 11. Kubernetes Manifests

```
infrastructure/kubernetes/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── service-account.yaml
├── services/
│   ├── api-gateway/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   └── hpa.yaml
│   ├── search-service/
│   ├── context-engine/
│   ├── llm-service/
│   ├── indexing-service/
│   └── embedding-service/
├── stateful/
│   ├── postgres/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   ├── redis/
│   └── qdrant/
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── alerts/
└── kustomization.yaml
```

### 12. Terraform

```
infrastructure/terraform/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   ├── elasticache/
│   └── s3/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── production/
└── README.md
```

---

## Development Workflow

### 13. Makefile

```makefile
# Development
.PHONY: setup
setup:
	@echo "Setting up development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	make migrate
	make seed

.PHONY: dev
dev:
	docker-compose -f docker-compose.dev.yml up

.PHONY: test
test:
	pytest tests/ -v --cov

.PHONY: lint
lint:
	black src/
	ruff check src/
	mypy src/

# Database
.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: seed
seed:
	python scripts/seed_database.py

# Docker
.PHONY: build
build:
	docker-compose build

.PHONY: push
push:
	docker-compose push

# Kubernetes
.PHONY: k8s-deploy
k8s-deploy:
	kubectl apply -k infrastructure/kubernetes/

.PHONY: k8s-delete
k8s-delete:
	kubectl delete -k infrastructure/kubernetes/
```

---

## File Templates

### 14. Service Template (FastAPI)

```python
# services/{service-name}/src/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from config import settings
from routes import router

app = FastAPI(
    title="{Service Name}",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Tracing
FastAPIInstrumentor.instrument_app(app)

@app.on_event("startup")
async def startup_event():
    # Initialize connections
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

### 15. Dockerfile Template

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
