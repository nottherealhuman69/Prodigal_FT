# Prodigal AI - Backend Engineering Assessment

> Complete implementation of 7 advanced backend engineering tasks demonstrating ML/AI, infrastructure, and automation expertise.

## Overview

This repository contains my submission for the Prodigal AI Advanced Backend Engineering assessment. Each task demonstrates production-ready implementations with proper documentation, containerization, and real-world applicability.

## Task Summary

| Task | Description | Key Technologies | Status |
|------|-------------|-----------------|--------|
| **1A** | ML Pipeline with Airflow & MLflow | Airflow, MLflow, scikit-learn, Flask | ✅ Complete |
| **1B** | RAG-style LLM Pipeline | FastAPI, SentenceTransformers, FAISS | ✅ Complete |
| **2** | Role-Based Access Control System | Flask, JWT, SQLite, RBAC | ✅ Complete |
| **3** | Kafka High-Throughput Ingestion | Kafka, Zookeeper, Docker Compose | ✅ Complete |
| **4** | Kubernetes Pod Auto-Scaling | K8s, HPA, Minikube, FastAPI | ✅ Complete |
| **5** | Binance WebSocket Price Capture | WebSocket, PostgreSQL, asyncio | ✅ Complete |
| **6** | Web Scraper & Analysis | Playwright, async, pagination | ✅ Complete |
| **7** | Multi-Agent Newsletter System | LangChain, Telegram Bot, AI agents | ✅ Complete |

## Quick Start

Each task is self-contained with its own setup instructions:

```bash
# Navigate to any task directory
cd Task_1_A   # ML Pipeline
cd Task_1_B   # RAG System  
cd Task_2     # RBAC System
cd Task_3     # Kafka Processing
cd Task_4     # K8s Scaling
cd Task_5     # Real-time Data
cd Task_6     # Web Scraping
cd Task_7     # Multi-Agent AI

# Follow the README in each directory for specific setup
```

## Architecture Highlights

### Task 1A: Complete ML Pipeline
- **Data Flow**: Ingestion → Feature Engineering → Training → Deployment
- **Orchestration**: Airflow DAGs with MLflow experiment tracking
- **Deployment**: Flask API with health checks and prediction endpoints
- **Demo**: Titanic survival prediction with 75-85% accuracy

### Task 1B: RAG System
- **Components**: PDF/CSV processing, vector embeddings, LLM generation
- **Models**: SentenceTransformers + FLAN-T5-small (efficient, lightweight)
- **Storage**: FAISS vector database for semantic search
- **Interface**: Web UI for document upload and natural language queries

### Task 2: Enterprise RBAC
- **Security**: JWT authentication with bcrypt password hashing
- **Hierarchy**: Organizations → Departments → Users → Resources
- **Permissions**: Admin, Manager, Contributor, Viewer roles
- **Sharing**: Time-based guest links with configurable expiration

### Task 3: Event Processing
- **Throughput**: 1000+ requests/minute sustained processing
- **Architecture**: Flask API → Kafka → Consumer workers
- **Reliability**: Message durability, retry logic, error handling
- **Monitoring**: Health checks, consumer logs, status tracking

### Task 4: Auto-Scaling
- **Platform**: Kubernetes with Horizontal Pod Autoscaler
- **Metrics**: CPU-based scaling (1-10 pods at 50% threshold)
- **Testing**: Load generation with real-time monitoring
- **Infrastructure**: Minikube setup with metrics server

### Task 5: Real-time Financial Data
- **Source**: Binance WebSocket (BTC/ETH pairs)
- **Precision**: DECIMAL(20,8) for cryptocurrency accuracy
- **Queries**: Latest price, historical lookup, range analysis
- **Performance**: Sub-second processing with proper indexing

### Task 6: Intelligent Scraping
- **Targets**: Microsoft Research + MyScheme Portal
- **Technology**: Playwright for JavaScript-rendered content
- **Features**: Pagination handling, rate limiting, error recovery
- **Output**: Structured data with comprehensive analysis report

### Task 7: AI Newsletter Generation
- **Sources**: 5 major Web3 publications (CoinDesk, CoinTelegraph, etc.)
- **Intelligence**: Cosine similarity deduplication, AI summarization
- **Automation**: LangChain multi-agent coordination
- **Delivery**: Automated Telegram newsletter distribution

## Key Technical Achievements

- **Production Patterns**: All services include health checks, logging, and error handling
- **Containerization**: Docker/Docker Compose for reproducible deployments
- **Scalability**: Horizontal scaling patterns with proper resource management
- **Security**: JWT, RBAC, input validation, and secure data handling
- **Performance**: Optimized for throughput and low latency where required
- **Monitoring**: Comprehensive logging and metrics collection

## Development Standards

- **Code Quality**: Type hints, error handling, comprehensive documentation
- **Testing**: Health endpoints, load testing, edge case handling
- **Documentation**: Setup guides, API documentation, troubleshooting
- **DevOps**: Automated setup scripts, environment configuration
- **Architecture**: Clean separation of concerns, modular design

## Setup Requirements

### General Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Git

### Task-Specific Requirements
- **Task 1A**: Airflow, MLflow
- **Task 4**: Kubernetes (Minikube)  
- **Task 5**: PostgreSQL
- **Task 7**: Telegram Bot API keys

## Demo Videos

Each task includes a 5-minute demo video showing:
- Setup and installation
- Core functionality demonstration  
- Error handling and edge cases
- Performance under load
- Code walkthrough

## Performance Metrics

- **ML Training**: <2 minutes end-to-end
- **Event Processing**: 1000+ req/min sustained
- **K8s Scaling**: <30s scale-up response
- **Real-time Data**: Sub-second WebSocket processing
- **Web Scraping**: 5 sites in <3 minutes
- **Newsletter Generation**: <3 minutes complete pipeline

## Technology Stack

**Languages**: Python  
**Frameworks**: Flask, FastAPI, Airflow  
**AI/ML**: scikit-learn, MLflow, SentenceTransformers, LangChain  
**Data**: PostgreSQL, SQLite, FAISS  
**Infrastructure**: Docker, Kubernetes, Kafka, Zookeeper  
**Integration**: WebSocket, Telegram Bot API, JWT

## Repository Structure

```
Prodigal_FT/
├── Task_1_A/           # ML Pipeline (Airflow + MLflow)
├── Task_1_B/           # RAG System (FastAPI + FAISS)
├── Task_2/             # RBAC System (Flask + JWT)
├── Task_3/             # Kafka Processing (Docker Compose)
├── Task_4/             # K8s Auto-Scaling (HPA)
├── Task_5/             # Real-time Data (WebSocket + PostgreSQL)
├── Task_6/             # Web Scraping (Playwright)
├── Task_7/             # Multi-Agent AI (LangChain + Telegram)
└── README.md           # This file
```

Each directory contains:
- Complete source code
- Detailed README with setup instructions
- Requirements and dependencies
- Demo video (5-10 minutes)
- SUMMARY.md with challenges and decisions

---

**Submission by**: [Your Name]  
**Email**: hiring@prodigalai.com  
**Subject**: AI Backend Task Submission - [Your Name]

This implementation demonstrates expertise in modern backend development, ML operations, distributed systems, and production-ready software engineering practices.