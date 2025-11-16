# Backend Structure Documentation - REFACTORED

## Overview
This document describes the **refactored** backend structure of the Admissions Counseling Chatbot system.
**MAJOR CHANGE**: Directory structure has been flattened to reduce complexity and improve maintainability.

## Directory Structure (REFACTORED)

```
backend/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration settings (using os.getenv)
│   │
│   ├── api/                       # FLATTENED API layer
│   │   ├── __init__.py
│   │   ├── chat.py               # Chat endpoints + schemas combined
│   │   └── health.py             # Health endpoints + schemas combined
│   │
│   ├── core/                      # FLATTENED core utilities
│   │   ├── __init__.py
│   │   ├── instances.py          # Singleton instances manager
│   │   ├── openai_logger.py      # OpenAI API logging
│   │   ├── elasticsearch.py      # Elasticsearch client (moved from database/)
│   │   └── mongodb.py            # MongoDB client (moved from database/)
│   │
│   ├── prompts/                   # Prompt engineering module (unchanged)
│   │   ├── __init__.py
│   │   ├── system_prompts.py     # System prompts for different scenarios
│   │   └── prompt_templates.py   # Prompt templates and formatting utilities
│   │
│   ├── services/                  # FLATTENED business logic layer
│   │   ├── __init__.py
│   │   ├── chat_service.py       # Chat business logic
│   │   ├── health_service.py     # Health check business logic
│   │   ├── search.py             # Hybrid search (moved from retrieval/)
│   │   ├── reranker.py           # Cross-encoder reranking (moved from retrieval/)
│   │   └── answer_generator.py   # OpenAI-based generation (moved from generation/)
│   │
│   └── workflows/                 # LangGraph workflows (unchanged)
│       ├── __init__.py
│       └── chatbot_workflow.py   # Main chatbot workflow
│
├── scripts/                       # Utility scripts
│   ├── __init__.py
│   ├── ingest_data.py            # Data ingestion script
│   ├── test_connections.py       # Test database connections
│   ├── test_search.py            # Test search and generation
│   ├── test_workflow.py          # Test LangGraph workflow (TODO)
│   └── test_api.py               # Test API endpoints (TODO)
│
├── logs/                          # Log files (gitignored)
├── requirements.txt               # Python dependencies
├── requirements-minimal.txt       # Minimal dependencies
└── STRUCTURE.md                   # This file
```

## Module Descriptions

### `app/api/` - API Layer (FLATTENED)
Contains combined FastAPI endpoints and Pydantic schemas.

**Key files:**
- `chat.py`: Main chat endpoints and schemas for user interactions
- `health.py`: Health check endpoint and schemas

### `app/core/` - Core Utilities (FLATTENED)
Shared components used across the application.

**Key files:**
- `elasticsearch.py`: Elasticsearch connection and utilities (moved from `database/`)
- `mongodb.py`: MongoDB connection and utilities (moved from `database/`)
- `instances.py`: Singleton manager for all major components (models, clients, etc.)

### `app/prompts/` - Prompt Engineering
Centralized prompt management for LLM interactions.

**Key files:**
- `system_prompts.py`: System prompts for different scenarios (default, clarification, validation)
- `prompt_templates.py`: Template functions for formatting prompts

**Why separate prompts?**
- Easy to modify and version control prompts
- Reusable across different services
- Clear separation of concerns

### `app/services/` - Business Logic (FLATTENED)
Core business logic for the chatbot system - all files moved to single directory.

**Key files:**
- `chat_service.py`: Main chat business logic and workflow orchestration
- `health_service.py`: System health checks and status reporting
- `search.py`: Hybrid search combining BM25 + Vector search (moved from `retrieval/`)
- `reranker.py`: Cross-encoder reranking for improved relevance (moved from `retrieval/`)
- `answer_generator.py`: OpenAI-based answer generation (moved from `generation/`)

### `app/workflows/` - LangGraph Workflows
LangGraph-based workflow orchestration for complex conversational flows.

**Planned nodes:**
1. Input Node: Parse and validate user query
2. Retrieval Node: Hybrid search + reranking
3. Context Building Node: Format retrieved documents
4. Generation Node: Generate answer with LLM
5. Validation Node: Check for hallucination and relevance
6. Output Node: Format final response

## Data Flow

### Simple Query Flow
```
User Query
    ↓
API Endpoint (chat.py)
    ↓
LangGraph Workflow (chatbot_workflow.py)
    ↓
Retrieval Service (search.py)
    ├─→ Elasticsearch (hybrid search)
    └─→ Reranker (cross-encoder)
    ↓
Generation Service (answer_generator.py)
    └─→ OpenAI API
    ↓
Response to User
```

### With Conversation History
```
User Query + Conversation ID
    ↓
API Endpoint (chat.py)
    ↓
Conversation Manager (manager.py)
    └─→ MongoDB (fetch history)
    ↓
LangGraph Workflow
    ├─→ Retrieval (with context)
    └─→ Generation (with history)
    ↓
Conversation Manager
    └─→ MongoDB (save turn)
    ↓
Response to User
```

## Configuration

Configuration is managed through environment variables (`.env` file) and loaded using `os.getenv()` in `config.py`.

**Key settings:**
- Database connections (Elasticsearch, MongoDB)
- OpenAI API key
- Embedding model
- Reranker settings
- Answer generation settings
- LangGraph settings (TODO)

## Testing

### Unit Tests
- Test individual components (search, reranker, answer generator)
- Located in `scripts/test_*.py`

### Integration Tests
- Test complete workflows
- Test API endpoints
- Located in `scripts/test_workflow.py` and `scripts/test_api.py`

## Refactoring Summary (2024)

### MAJOR CHANGES - Directory Flattening
The backend structure has been significantly simplified by flattening nested directories:

**API Layer Changes:**
- `app/api/routes/` + `app/api/schemas/` → `app/api/` (combined routes + schemas)
- Reduced from 3 levels to 2 levels of nesting

**Core Layer Changes:**
- `app/core/database/` → `app/core/` (moved database files up one level)
- Reduced from 3 levels to 2 levels of nesting

**Services Layer Changes:**
- `app/services/retrieval/` → `app/services/` (flattened retrieval services)
- `app/services/generation/` → `app/services/` (flattened generation services)
- `app/services/conversation/` → `app/services/` (flattened conversation services)
- Reduced from 3 levels to 2 levels of nesting

### Updated Import Paths
```python
# OLD IMPORTS (before refactoring)
from app.api.routes.chat import router as chat_router
from app.api.schemas.chat import ChatQueryRequest
from app.core.database.elasticsearch import get_elasticsearch_client
from app.core.database.mongodb import get_mongodb_client
from app.services.retrieval.search import get_search_engine
from app.services.retrieval.reranker import get_reranker
from app.services.generation.answer_generator import get_answer_generator

# NEW IMPORTS (after refactoring)
from app.api.chat import router as chat_router, ChatQueryRequest
from app.api.health import router as health_router
from app.core.elasticsearch import get_elasticsearch_client
from app.core.mongodb import get_mongodb_client
from app.services.search import get_search_engine
from app.services.reranker import get_reranker
from app.services.answer_generator import get_answer_generator
```

### Benefits of Refactoring
1. **Reduced Complexity**: Directory depth reduced from 4 levels to 2-3 levels maximum
2. **Improved Navigation**: Related files are easier to find and access
3. **Simplified Imports**: Shorter, more intuitive import paths
4. **Better Maintainability**: Less directory overhead, easier to reorganize
5. **Preserved Functionality**: All API endpoints and functionality remain unchanged

## TODO
- [ ] Implement LangGraph workflow (`app/workflows/`)
- [ ] Implement conversation manager (`app/services/conversation/manager.py`)
- [ ] Implement API endpoints (`app/api/routes/`)
- [ ] Implement API schemas (`app/api/schemas/`)
- [ ] Add logging configuration (`app/core/logging.py`)
- [ ] Add authentication and rate limiting (`app/api/deps.py`)
- [ ] Write test scripts (`scripts/test_workflow.py`, `scripts/test_api.py`)
- [ ] Add comprehensive documentation

## Best Practices

1. **Separation of Concerns**: Each module has a clear responsibility
2. **Dependency Injection**: Use factory functions (e.g., `get_search_engine()`)
3. **Configuration Management**: Centralized in `config.py` using environment variables
4. **Prompt Engineering**: Separate prompts from code for easy modification
5. **Error Handling**: Graceful fallbacks (e.g., extractive answer when generation fails)
6. **Logging**: Comprehensive logging for debugging and monitoring
7. **Testing**: Test each component independently and as a whole

## References
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/
- LangGraph: https://langchain-ai.github.io/langgraph/
- Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- MongoDB: https://www.mongodb.com/docs/

