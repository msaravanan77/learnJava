.PHONY: help setup dev test lint clean build deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "Setting up development environment..."
	@cp -n .env.example .env 2>/dev/null || true
	@echo "Installing Python dependencies..."
	@pip install -r services/embedding-service/requirements.txt
	@pip install -r services/search-service/requirements.txt
	@pip install -r services/indexing-service/requirements.txt
	@echo "Starting Docker services..."
	@docker-compose up -d qdrant postgres redis
	@echo "✅ Setup complete!"

dev: ## Start all services in development mode
	@echo "Starting all services..."
	@docker-compose -f docker-compose.yml up

dev-bg: ## Start all services in background
	@docker-compose up -d
	@echo "✅ Services started in background"
	@echo "Run 'make logs' to view logs"

stop: ## Stop all services
	@docker-compose down
	@echo "✅ Services stopped"

restart: ## Restart all services
	@make stop
	@make dev-bg

logs: ## View logs from all services
	@docker-compose logs -f

logs-service: ## View logs from specific service (usage: make logs-service SERVICE=search-service)
	@docker-compose logs -f $(SERVICE)

ps: ## Show running services
	@docker-compose ps

test: ## Run all tests
	@echo "Running tests..."
	@pytest tests/ -v --cov --cov-report=term-missing

test-unit: ## Run unit tests only
	@pytest tests/unit/ -v

test-integration: ## Run integration tests
	@pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@pytest tests/e2e/ -v

test-service: ## Test specific service (usage: make test-service SERVICE=search-service)
	@cd services/$(SERVICE) && pytest tests/ -v

lint: ## Run linters
	@echo "Running linters..."
	@black services/ --check
	@ruff check services/
	@mypy services/

format: ## Format code
	@echo "Formatting code..."
	@black services/
	@echo "✅ Code formatted"

clean: ## Clean up generated files and caches
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

build: ## Build Docker images
	@echo "Building Docker images..."
	@docker-compose build
	@echo "✅ Images built"

build-service: ## Build specific service (usage: make build-service SERVICE=search-service)
	@docker-compose build $(SERVICE)
	@echo "✅ $(SERVICE) image built"

migrate: ## Run database migrations
	@echo "Running migrations..."
	@docker-compose exec postgres psql -U admin -d workspace_intelligence -f /docker-entrypoint-initdb.d/schema.sql
	@echo "✅ Migrations complete"

seed: ## Seed database with sample data
	@echo "Seeding database..."
	@python scripts/seed_database.py
	@echo "✅ Database seeded"

shell-service: ## Open shell in service container (usage: make shell-service SERVICE=search-service)
	@docker-compose exec $(SERVICE) /bin/bash

shell-db: ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U admin -d workspace_intelligence

shell-redis: ## Open Redis CLI
	@docker-compose exec redis redis-cli

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8001/health || echo "❌ Search service down"
	@curl -s http://localhost:8002/health || echo "❌ Embedding service down"
	@curl -s http://localhost:6333/health || echo "❌ Qdrant down"
	@docker-compose exec postgres pg_isready -U admin || echo "❌ PostgreSQL down"
	@docker-compose exec redis redis-cli ping || echo "❌ Redis down"

k8s-deploy: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	@kubectl apply -k infrastructure/kubernetes/
	@echo "✅ Deployment started"

k8s-status: ## Check Kubernetes deployment status
	@kubectl get pods -n workspace-intelligence

k8s-logs: ## View Kubernetes logs (usage: make k8s-logs SERVICE=search-service)
	@kubectl logs -n workspace-intelligence -l app=$(SERVICE) -f

k8s-delete: ## Delete Kubernetes deployment
	@kubectl delete -k infrastructure/kubernetes/

docs-serve: ## Serve documentation locally
	@python -m http.server 8000 --directory docs/
	@echo "📚 Documentation available at http://localhost:8000"

bench: ## Run performance benchmarks
	@python scripts/benchmark.py

monitor: ## Open monitoring dashboards
	@echo "Opening Grafana..."
	@open http://localhost:3000 || xdg-open http://localhost:3000
	@echo "Opening Qdrant Dashboard..."
	@open http://localhost:6333/dashboard || xdg-open http://localhost:6333/dashboard

install-dev-tools: ## Install development tools
	@pip install black ruff mypy pytest pytest-cov pytest-asyncio
	@echo "✅ Development tools installed"

ci: ## Run CI checks (lint + test)
	@make lint
	@make test

pre-commit: ## Run pre-commit checks
	@make format
	@make lint
	@make test-unit

quick-test: ## Run quick smoke tests
	@pytest tests/ -v -m "not slow"

version: ## Show version information
	@echo "Workspace Intelligence v1.0.0"
	@echo "Python: $(shell python --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "Docker Compose: $(shell docker-compose --version)"
