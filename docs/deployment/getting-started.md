# Getting Started - Local Development Setup

This guide will help you set up the Workspace Intelligence system on your local machine for development.

## Prerequisites

### Required Software
- **Docker** (20.10+) & **Docker Compose** (2.0+)
- **Git**
- **Python** 3.11+
- **Node.js** 18+ (for IDE extensions)
- **Make** (optional, for convenience commands)

### Recommended
- **NVIDIA GPU** with CUDA 11.8+ (for embedding service)
- **16GB RAM** minimum (32GB recommended)
- **50GB** free disk space

---

## Quick Start (5 Minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/workspace-intelligence.git
cd workspace-intelligence
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Database
DB_PASSWORD=your_secure_password

# API Keys (for LLM service)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Use local models instead
USE_LOCAL_LLM=false

# Services Configuration
EMBEDDING_MODEL=microsoft/graphcodebert-base
DEVICE=cuda  # or 'cpu' if no GPU
```

### 3. Start Services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- Qdrant (Vector DB) - Port 6333
- PostgreSQL - Port 5432
- Redis - Port 6379
- Embedding Service - Port 8002
- Search Service - Port 8001
- Indexing Service - Port 8000

### 4. Verify Services

```bash
# Check all services are running
docker-compose ps

# Check API health
curl http://localhost:8001/health

# Check Qdrant
curl http://localhost:6333/health
```

### 5. Initialize Database

```bash
# Run migrations
docker-compose exec postgres psql -U admin -d workspace_intelligence -f /docker-entrypoint-initdb.d/schema.sql

# Verify
docker-compose exec postgres psql -U admin -d workspace_intelligence -c "\dt"
```

---

## Development Workflow

### Running Individual Services

#### Embedding Service

```bash
cd services/embedding-service

# Install dependencies
pip install -r requirements.txt

# Run service
python -m uvicorn src.main:app --reload --port 8002
```

#### Search Service

```bash
cd services/search-service

pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8001
```

#### Indexing Service

```bash
cd services/indexing-service

pip install -r requirements.txt
python -m src.main
```

---

## Testing the System

### 1. Index a Sample Workspace

```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-workspace",
    "root_path": "/path/to/your/code"
  }'
```

Save the `workspace_id` from the response.

### 2. Trigger Indexing

```bash
curl -X POST http://localhost:8000/api/v1/workspaces/{workspace_id}/index
```

### 3. Check Indexing Status

```bash
curl http://localhost:8000/api/v1/workspaces/{workspace_id}/status
```

### 4. Perform a Search

```bash
curl -X POST http://localhost:8001/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "{workspace_id}",
    "query": "function that handles authentication",
    "limit": 5
  }'
```

---

## Development Tools

### Using Make Commands

```bash
# Setup environment
make setup

# Start all services
make dev

# Run tests
make test

# Lint code
make lint

# Stop services
make down

# Clean up
make clean
```

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U admin -d workspace_intelligence

# Redis
docker-compose exec redis redis-cli

# Qdrant Dashboard
open http://localhost:6333/dashboard
```

---

## Troubleshooting

### Services Won't Start

**Problem**: Docker containers failing to start

```bash
# Check logs
docker-compose logs -f [service-name]

# Common issues:
# 1. Port already in use
sudo lsof -i :6333  # Check Qdrant port
sudo lsof -i :5432  # Check PostgreSQL port

# 2. Insufficient resources
docker system prune  # Clean up Docker resources
```

### Embedding Service Crashes

**Problem**: Out of memory when loading models

**Solution**:
1. Reduce batch size in `embedding-service/src/config.py`
2. Use smaller model: `sentence-transformers/all-MiniLM-L6-v2`
3. Switch to CPU mode: `DEVICE=cpu` in `.env`

### Database Connection Errors

**Problem**: Cannot connect to PostgreSQL

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Slow Indexing

**Problem**: Indexing taking too long

**Solutions**:
1. Enable incremental indexing (only changed files)
2. Increase worker pool size
3. Use GPU for embedding generation
4. Reduce embedding model size

---

## Next Steps

1. **IDE Extension Setup**: See [VSCode Extension Guide](../user-guides/vscode-extension.md)
2. **Production Deployment**: See [Kubernetes Deployment](./kubernetes-deployment.md)
3. **API Documentation**: See [API Reference](../api/openapi-spec.yaml)

---

## Useful Commands Reference

```bash
# Docker Compose
docker-compose up -d                 # Start all services
docker-compose down                  # Stop all services
docker-compose logs -f [service]     # View logs
docker-compose ps                    # List services
docker-compose restart [service]     # Restart service

# Database
docker-compose exec postgres psql -U admin -d workspace_intelligence
docker-compose exec redis redis-cli

# Python Services
cd services/[service-name]
pip install -r requirements.txt
python -m uvicorn src.main:app --reload

# Tests
pytest tests/ -v --cov
pytest tests/test_search.py -v

# Linting
black src/
ruff check src/
mypy src/
```

---

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_PASSWORD` | PostgreSQL password | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | For LLM |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | For LLM |
| `QDRANT_URL` | Qdrant connection URL | `http://localhost:6333` | No |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` | No |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` | No |
| `EMBEDDING_MODEL` | Embedding model name | `microsoft/graphcodebert-base` | No |
| `DEVICE` | Device for ML (cpu/cuda) | `cuda` | No |

---

**Last Updated**: 2025-11-17
