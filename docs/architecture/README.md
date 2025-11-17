# Architecture Documentation

This directory contains comprehensive architecture documentation for the Workspace Intelligence System.

## 📊 Architecture Diagrams

### 1. [High-Level Architecture](./01-high-level-architecture.svg)
**Audience:** Executive Leadership, Product Managers, Technical Leadership

Shows the overall system structure with four main layers:
- **Client Layer**: IDE extensions, web clients, CLI tools
- **API Gateway Layer**: Authentication, rate limiting, load balancing
- **Service Layer**: Microservices (indexing, embedding, search, context, LLM, analytics)
- **Data Layer**: Qdrant (vectors), PostgreSQL (metadata), Redis (cache), Elasticsearch
- **External Services**: OpenAI, Anthropic Claude, local models

**Key Insights:**
- Layered architecture for separation of concerns
- Multiple client support (VSCode, IntelliJ, Web, CLI)
- Microservices-based for scalability
- Multi-database approach (polyglot persistence)

---

### 2. [Solution Architecture](./02-solution-architecture.svg)
**Audience:** Solution Architects, Senior Engineers, DevOps Engineers

End-to-end flow from code indexing to AI completion:

**Processing Pipeline:**
1. **Indexing Service** → Parse code with Tree-sitter → Extract elements
2. **Embedding Service** → Generate 768D vectors with GraphCodeBERT
3. **Vector DB** → Store embeddings in Qdrant with HNSW index

**Query Pipeline:**
4. **Search Service** → Semantic + hybrid search → Re-ranking
5. **Context Engine** → Gather code + traverse dependencies → Optimize tokens
6. **LLM Service** → Call external AI (OpenAI/Claude) → Stream response

**Key Metrics Included:**
- ⚡ Indexing: <5 sec/1000 files
- 🔍 Search: <100ms p95 latency
- 🤖 Completion: <200ms first token
- 🌐 Scale: 10,000+ concurrent users
- 🛡️ Security: E2E encryption
- 📈 Uptime: 99.9% SLA

---

### 3. [Component Connectivity & Data Flow](./03-component-connectivity-flow.svg)
**Audience:** Backend Engineers, System Integrators, Technical Architects

Detailed view of how microservices communicate:

**Service Ports:**
- API Gateway: 8080
- Indexing Service: 8000
- Search Service: 8001
- Embedding Service: 8002
- Context Engine: 8003
- LLM Service: 8004
- Analytics: 8005

**Communication Patterns:**
- **Sync (REST)**: Green solid arrows - Request/response
- **Async (Events)**: Blue dashed arrows - Event-driven
- **Message Queue**: Red dotted arrows - Queue-based processing
- **Data Access**: Purple lines - Database queries

**Key Data Flows:**
1. 📝 **Code Indexing**: IDE → Gateway → Indexing → Queue → Embedding → Qdrant
2. 🔍 **Code Search**: IDE → Gateway → Search → Embedding (query) → Qdrant → IDE
3. 🤖 **AI Completion**: IDE → Gateway → Context → Search + PostgreSQL → LLM → External AI → IDE
4. 📊 **Monitoring**: All Services → Prometheus + Jaeger + ELK → Grafana → Alerts

**Monitoring Stack:**
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking

---

### 4. [Network & Deployment Architecture](./04-network-deployment-diagram.svg)
**Audience:** DevOps Engineers, SREs, Security Engineers, Cloud Architects

Production Kubernetes deployment across multiple availability zones:

**Infrastructure Layers:**

**🌐 Internet / Public Zone:**
- CloudFront CDN for static assets
- Route 53 DNS with health checks and failover
- WAF + DDoS protection (AWS Shield)
- Certificate Manager for SSL/TLS

**⚖️ Load Balancer Layer:**
- Application Load Balancer (ALB) - Multi-AZ
- HTTPS (443) + WebSocket (WSS) support
- Health checks + sticky sessions
- SSL termination

**☸️ Kubernetes Cluster (VPC: 10.0.0.0/16):**

**Availability Zone A (us-east-1a) - Subnet: 10.0.1.0/24:**
- **Namespace: workspace-intelligence**
  - API Gateway: 3 replicas, 1 CPU, 2 GB RAM
  - Search Service: 3 replicas (HPA: 3-10), 2 CPU, 4 GB RAM
  - Context Engine: 2 replicas, 1 CPU, 2 GB RAM
  - LLM Service: 2 replicas, 2 CPU, 4 GB RAM

- **Namespace: ml-services (GPU Node Pool)**
  - Embedding Service: 2 replicas, 1x NVIDIA T4 GPU, 4 CPU, 8 GB RAM
  - Indexing Service: 2 replicas, 2 CPU, 4 GB RAM
  - Worker Pods (Celery): 5 replicas (auto-scaling)

**Availability Zone B (us-east-1b) - Subnet: 10.0.2.0/24:**
- Mirror of AZ-A for High Availability
- All services replicated across zones
- Automatic failover

**💾 Data Layer - Managed Services (Multi-AZ):**
- **RDS PostgreSQL**: db.r5.large, Primary + Standby
- **ElastiCache Redis**: cache.r5.large, 3-node cluster
- **Qdrant Cloud**: 100M vectors, HA cluster
- **S3**: Files, models, backups (11 9's durability)
- **Elasticsearch**: 3-node cluster for logs

**Security:**
- 🔒 VPC isolation with private subnets
- Security groups for network segmentation
- Encryption at rest and in transit
- IAM roles for service authentication

---

### 5. [Data Flow Sequence Diagram](./05-data-flow-sequence.svg)
**Audience:** Software Engineers, QA Engineers, Performance Engineers

Step-by-step sequence of a code completion request:

**Timeline (200ms total):**

**t=0ms:** Developer types code in IDE
**t=5ms:**
1. IDE → API Gateway: `POST /api/v1/completion`
2. API Gateway validates JWT token

**t=20ms:**
3. Gateway → Context Engine: Request context
4. Context analyzes current file and cursor position
5-7. Context → Search → Embedding: Get query embedding (768D vector)
8-9. Search → Qdrant: Similarity search using HNSW index
10. Qdrant returns top 10 similar code snippets

**t=50ms:**
11-12. Context → PostgreSQL: Query dependency graph for related files
13. Context builds complete prompt:
   - Current file context
   - Similar code from search
   - Dependencies and imports
   - Token optimization (fit in ~3500 tokens)

**t=100ms:**
14. Context → Gateway: Return optimized context
15. Gateway → LLM Service: Generate completion request
16. LLM → OpenAI: API call with context + prompt

**t=200ms:**
17-19. OpenAI streams tokens → LLM → Gateway → IDE via WebSocket

**Performance Breakdown:**
- Context gathering: 50ms
- Database queries: 30ms
- LLM first token: 100ms
- Network overhead: 20ms
- **Total**: ~200ms

---

## 🏗️ Architecture Principles

### 1. **Microservices Architecture**
- Independent services with clear boundaries
- Each service owns its data
- Communication via REST APIs and message queues
- Independently deployable and scalable

### 2. **Event-Driven Design**
- Async processing for non-blocking operations
- Message queues (Redis/RabbitMQ) for job distribution
- Event streaming for real-time updates

### 3. **Polyglot Persistence**
- **Qdrant**: Vector embeddings (similarity search)
- **PostgreSQL**: Structured metadata, relationships, graphs
- **Redis**: Caching, sessions, rate limiting, message queue
- **Elasticsearch**: Keyword search, logs
- **S3**: Object storage for files and backups

### 4. **High Availability**
- Multi-AZ deployment for fault tolerance
- Service replication with horizontal pod autoscaling
- Health checks and automatic failover
- Data replication across zones

### 5. **Security First**
- Zero-trust network architecture
- Encryption at rest and in transit
- JWT-based authentication
- RBAC for authorization
- VPC isolation with private subnets
- WAF and DDoS protection

### 6. **Observability**
- Comprehensive monitoring (Prometheus + Grafana)
- Distributed tracing (Jaeger)
- Centralized logging (ELK Stack)
- Error tracking (Sentry)
- Real-time alerting

### 7. **Scalability**
- Horizontal scaling for stateless services
- Vertical scaling for databases
- Auto-scaling based on metrics (CPU, memory, queue depth)
- Caching at multiple layers
- CDN for static assets

---

## 📐 Design Patterns Used

### Service Layer
- **API Gateway Pattern**: Centralized entry point
- **Service Registry Pattern**: Dynamic service discovery
- **Circuit Breaker Pattern**: Fault tolerance
- **Retry Pattern**: Transient failure handling
- **Bulkhead Pattern**: Resource isolation

### Data Layer
- **CQRS**: Separate read/write models
- **Event Sourcing**: For audit trails
- **Cache-Aside**: On-demand caching
- **Sharding**: Horizontal data partitioning

### Integration
- **Adapter Pattern**: LLM provider abstraction
- **Strategy Pattern**: Search algorithms
- **Factory Pattern**: Service instantiation
- **Observer Pattern**: Event notifications

---

## 🔄 Data Flow Patterns

### Indexing Flow (Write Path)
```
Source Code → File Watcher → Indexing Service → Parser (Tree-sitter)
  → Extract Elements → Embedding Service → Generate Vectors
  → Qdrant (vectors) + PostgreSQL (metadata)
```

### Search Flow (Read Path)
```
User Query → Search Service → Embedding Service (query embedding)
  → Qdrant (similarity search) → Re-ranking → Results
  → Cache (Redis) for future queries
```

### Completion Flow (AI Path)
```
User Input → Context Engine → [Search + Dependency Graph]
  → Build Context → LLM Service → External AI API
  → Stream Response → User
```

---

## 🎯 Non-Functional Requirements

### Performance
- **Search Latency**: p95 < 100ms, p99 < 200ms
- **Completion Latency**: First token < 200ms
- **Indexing Throughput**: 1000 files/sec
- **Embedding Generation**: < 50ms per element

### Scalability
- **Concurrent Users**: 10,000+
- **Queries per Second**: 1,000+
- **Indexed Code Elements**: 100M+
- **Workspace Size**: Up to 1M files

### Reliability
- **Uptime**: 99.9% SLA (< 43 minutes/month downtime)
- **Data Durability**: 99.999999999% (11 9's)
- **Recovery Time Objective (RTO)**: < 15 minutes
- **Recovery Point Objective (RPO)**: < 5 minutes

### Security
- **Compliance**: SOC 2 Type II, GDPR, HIPAA-ready
- **Authentication**: OAuth 2.0, SAML, SSO
- **Authorization**: RBAC with fine-grained permissions
- **Encryption**: TLS 1.3, AES-256 at rest

---

## 📚 Related Documentation

- **API Documentation**: See `/docs/api/`
- **Deployment Guide**: See `/docs/deployment/`
- **User Guides**: See `/docs/user-guides/`
- **Technical Specifications**: See `/TECHNICAL_SPECIFICATIONS.md`
- **Project Structure**: See `/PROJECT_STRUCTURE.md`

---

## 🤝 Contributing to Architecture

When proposing architecture changes:
1. Create an Architecture Decision Record (ADR)
2. Update relevant diagrams
3. Document impact on existing components
4. Review with architecture team
5. Update this README

---

**Last Updated**: 2025-11-17
**Version**: 1.0
**Maintained By**: Engineering Team
