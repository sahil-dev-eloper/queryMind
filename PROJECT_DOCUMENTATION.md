# QueryMind — Complete Project Documentation

> **QueryMind** is a full-stack, natural-language analytics application for PostgreSQL databases.
> Users connect a database, inspect its schema, ask questions in plain English, and receive safe SQL, real query results, summaries, and dynamic visualizations — all without writing a single line of SQL.

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure (File Tree)](#3-project-structure-file-tree)
4. [Infrastructure and Deployment](#4-infrastructure-and-deployment)
5. [Database Layer](#5-database-layer)
6. [Backend (FastAPI)](#6-backend-fastapi)
7. [The Query Pipeline — End-to-End Flow](#7-the-query-pipeline--end-to-end-flow)
8. [Frontend (React + Vite)](#8-frontend-react--vite)
9. [Security Model](#9-security-model)
10. [Testing](#10-testing)
11. [Evaluation Dataset](#11-evaluation-dataset)
12. [How to Run](#12-how-to-run)

---

## 1. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                           USER (Browser)                             │
│   React SPA (Vite + TypeScript + Tailwind + Recharts + Lucide)       │
└────────────────────────────┬───────────────────────────────────────────┘
                             │  HTTP / JSON
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                        │
│  ┌──────────┐  ┌───────────────────┐  ┌─────────────────────────┐    │
│  │ API      │→ │ Query Pipeline    │→ │ AI Module               │    │
│  │ Routers  │  │ (Orchestrator)    │  │ (Mock / OpenAI Provider)│    │
│  └──────────┘  └────────┬──────────┘  └─────────────────────────┘    │
│                         │                                            │
│  ┌──────────────────────┼────────────────────────────────────────┐   │
│  │  Service Layer       │                                        │   │
│  │  • Schema Retriever  • Clarification Engine                   │   │
│  │  • SQL Validator     • Query Executor                         │   │
│  │  • SQL Repair        • Result Analyzer                        │   │
│  │  • Intent Modifier   • Error Classification                   │   │
│  │  • Credential Svc    • Schema Introspection                   │   │
│  └──────────────────────┼────────────────────────────────────────┘   │
│                         │                                            │
│           ┌─────────────┴──────────────┐                             │
│           ▼                            ▼                             │
│  ┌──────────────────┐       ┌────────────────────┐                   │
│  │ App PostgreSQL   │       │ External PostgreSQL │                   │
│  │ (QueryMind data) │       │ (User's database)   │                   │
│  └──────────────────┘       └────────────────────┘                   │
└────────────────────────────────────────────────────────────────────────┘
```

**Two databases** are in play:

| Database | Purpose |
|---|---|
| **Application DB** (`querymind` on port 5432) | Stores QueryMind's own data: connections, schemas, conversations, messages, clarifications, query executions. |
| **External / User DB** (e.g. `analytics` on port 5433) | The user-connected PostgreSQL database. Only used for schema inspection and **read-only** query execution. |

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite 6, Tailwind CSS 3, React Router 7, TanStack Query 5, Recharts 3, Lucide React |
| **Backend** | Python 3.12, FastAPI 0.115+, Pydantic 2.11+, SQLAlchemy 2.0+, Alembic 1.14 |
| **AI** | Mock provider (deterministic local dev), OpenAI-compatible provider (via `httpx`) |
| **SQL Parsing** | `sqlglot` 26+ |
| **Encryption** | `cryptography` (Fernet symmetric encryption) |
| **Databases** | PostgreSQL 16 (Alpine images) |
| **Infrastructure** | Docker, Docker Compose |

---

## 3. Project Structure (File Tree)

```
QueryMind/
├── .env.example                    # Environment variable template
├── .gitignore
├── README.md                       # Project README
├── docker-compose.yml              # Multi-service orchestration
│
├── backend/
│   ├── Dockerfile                  # Python 3.12-slim image
│   ├── requirements.txt            # Python dependencies
│   ├── alembic.ini                 # Alembic config
│   ├── alembic/
│   │   ├── env.py                  # Migration environment (reads app config)
│   │   ├── script.py.mako          # Migration template
│   │   └── versions/               # Migration scripts
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app creation, middleware, routers
│   │   ├── ai/
│   │   │   ├── __init__.py         # Re-exports
│   │   │   ├── models.py           # Pydantic models: QueryAnalysis, SQLGenerationResult
│   │   │   ├── provider.py         # Abstract AIProvider base class
│   │   │   ├── factory.py          # get_ai_provider() factory
│   │   │   ├── mock_provider.py    # Deterministic mock for local dev
│   │   │   ├── openai_provider.py  # Real OpenAI API integration
│   │   │   └── prompts/
│   │   │       ├── query_analysis.py
│   │   │       ├── sql_generation.py
│   │   │       ├── clarification_detection.py
│   │   │       ├── clarification_question.py
│   │   │       └── clarification_answer.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py           # GET /api/health, GET /api/health/database
│   │   │   ├── databases.py        # CRUD + test/introspect/schema for connections
│   │   │   └── queries.py          # Query execution, conversations, clarifications
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings (env vars)
│   │   │   ├── errors.py           # Global exception handler
│   │   │   ├── logging.py          # Structured logging with ContextFormatter
│   │   │   └── security.py         # SHA-256 hash utility
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # SQLAlchemy DeclarativeBase
│   │   │   └── session.py          # Engine, SessionLocal, get_db() dependency
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── database.py         # All ORM models (9 tables)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── databases.py        # Request/Response schemas for database CRUD
│   │   │   ├── queries.py          # QueryRequest, QueryResponse
│   │   │   └── clarifications.py   # Clarification, Conversation schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── query_pipeline.py       # Central orchestrator (the "brain")
│   │       ├── clarification.py        # Question generator + answer processor
│   │       ├── clarification_state.py  # ConversationState enum
│   │       ├── credentials.py          # Fernet encrypt/decrypt
│   │       ├── external_database.py    # Connect to user's PostgreSQL
│   │       ├── schema_introspection.py # Live schema discovery via Inspector
│   │       ├── schema_retriever.py     # Deterministic keyword-to-table ranking
│   │       ├── schema_serializer.py    # ORM models to JSON schema dict
│   │       ├── sql_validator.py        # Read-only + schema validation via sqlglot
│   │       ├── sql_repair.py           # Bounded SQL repair
│   │       ├── query_executor.py       # Execute SQL against external DB
│   │       ├── result_analyzer.py      # Column type analysis + chart recommendation
│   │       ├── error_classification.py # Categorize DB errors
│   │       └── intent_modifier.py      # Apply follow-up mutations to intent
│   └── tests/
│       ├── test_health.py
│       ├── test_phase1.py
│       ├── test_ai_pipeline.py
│       ├── test_clarification.py
│       ├── test_intelligence.py
│       └── test_query_safety.py
│
├── demo/
│   ├── Dockerfile                  # postgres:16-alpine + init.sql
│   └── init.sql                    # 6 tables + seed data
│
├── evaluation/
│   └── queries.json                # 47 behavior test cases
│
└── frontend/
    ├── Dockerfile                  # node:22-alpine
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    ├── public/
    └── src/
        ├── main.tsx                # React root + providers
        ├── App.tsx                 # Shell layout + routing
        ├── styles.css              # Global styles
        ├── database.css            # Database page styles
        ├── phase5.css              # Visualization + clarification styles
        ├── vite-env.d.ts
        ├── services/
        │   └── api.ts              # Generic fetch wrapper (apiRequest)
        ├── pages/
        │   ├── Dashboard.tsx       # Main query workspace
        │   ├── DatabasePage.tsx    # Database connection management
        │   ├── ConversationsPage.tsx # Conversation history
        │   └── PlaceholderPage.tsx  # Generic placeholder
        ├── components/
        │   ├── ClarificationCard.tsx   # Disambiguation UI
        │   ├── ResultTable.tsx         # Tabular data display
        │   ├── ResultVisualization.tsx  # Line/Bar chart (Recharts)
        │   ├── SQLViewer.tsx           # Collapsible SQL display with copy
        │   └── SchemaExplorer.tsx      # Tree + detail view for schema
        ├── hooks/
        │   └── useDatabases.ts     # (stub)
        ├── types/
        │   └── database.ts         # (stub)
        └── lib/
            └── .gitkeep
```

---

## 4. Infrastructure and Deployment

### 4.1 Docker Compose

The `docker-compose.yml` defines **four services**:

| Service | Image | Ports | Role |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | `5432:5432` | Application database (QueryMind data) |
| `demo-postgres` | Custom build (`./demo`) | `5433:5432` | Seeded demo analytics database |
| `backend` | Custom build (`./backend`) | `8000:8000` | FastAPI server |
| `frontend` | Custom build (`./frontend`) | `5173:5173` | Vite dev server |

**Key behaviors:**
- The `backend` container runs `alembic upgrade head && uvicorn ...` on startup — migrations are automatic.
- The `backend` depends on `postgres` (health check: `pg_isready`).
- The `frontend` depends on `backend`.
- A named volume `postgres_data` persists the application database.

### 4.2 Dockerfiles

**Backend** (`backend/Dockerfile`):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend** (`frontend/Dockerfile`):
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Demo DB** (`demo/Dockerfile`):
```dockerfile
FROM postgres:16-alpine
COPY init.sql /docker-entrypoint-initdb.d/001_init.sql
```
The `init.sql` is automatically executed when the container starts for the first time (PostgreSQL entrypoint behavior).

### 4.3 Environment Configuration

All configuration is driven by `.env` (copied from `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `development` | Environment name |
| `DATABASE_URL` | `postgresql+psycopg://querymind:querymind@localhost:5432/querymind` | Application DB connection string |
| `SECRET_KEY` | `replace-with-a-long-random-value` | Key for Fernet credential encryption |
| `AI_PROVIDER` | `mock` | `mock` or `openai` |
| `AI_API_KEY` | _(empty)_ | Required when `AI_PROVIDER=openai` |
| `AI_MODEL` | _(empty)_ | OpenAI model name (e.g., `gpt-4`) |
| `MAX_QUERY_ROWS` | `1000` | Max rows returned from external queries |
| `QUERY_TIMEOUT_SECONDS` | `10` | PostgreSQL `statement_timeout` |
| `MAX_SQL_REPAIR_ATTEMPTS` | `2` | How many times to attempt SQL auto-repair |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |

Settings are loaded via `pydantic-settings` in `app/core/config.py`. The `Settings` class reads from environment variables and `.env` file, and is cached with `@lru_cache`.

---

## 5. Database Layer

### 5.1 Application Database (QueryMind PostgreSQL)

The application's own PostgreSQL database (`querymind`) stores **9 tables** managed by SQLAlchemy ORM models:

| Table | Purpose |
|---|---|
| `database_connections` | Stored external database connection metadata (host, port, encrypted password, etc.) |
| `database_schemas` | Persisted schema names (e.g., `public`) from introspected databases |
| `database_tables` | Tables discovered during introspection |
| `database_columns` | Columns of each table (name, type, nullable, PK, default) |
| `database_relationships` | Foreign key relationships between tables |
| `conversations` | Multi-turn conversation sessions |
| `messages` | Individual messages within conversations (user and assistant) |
| `clarifications` | Disambiguation questions + answers within a conversation |
| `query_executions` | Full execution records (SQL, status, timing, result analysis, repair info) |

### 5.2 Demo Database (Seeded Analytics)

The demo database (`analytics`, port 5433) is created via `demo/init.sql` with **6 tables**:

| Table | Key Columns | Relationships |
|---|---|---|
| `categories` | `id`, `name` | — |
| `regions` | `id`, `name` | — |
| `customers` | `id`, `name`, `email`, `region_id`, `created_at` | FK to `regions(id)` |
| `products` | `id`, `name`, `category_id`, `price` | FK to `categories(id)` |
| `orders` | `id`, `customer_id`, `order_date`, `total_amount` | FK to `customers(id)` |
| `order_items` | `id`, `order_id`, `product_id`, `quantity`, `unit_price` | FK to `orders(id)`, `products(id)` |

**Seed data**: 3 categories, 3 regions, 3 customers, 3 products, 3 orders, 4 order items.

### 5.3 SQLAlchemy Models

All models live in `backend/app/models/database.py` and extend `Base` (from `app/db/base.py`):

```python
class Base(DeclarativeBase):
    pass
```

**Key model relationships:**
- `DatabaseConnection` has many `DatabaseSchema` and `Conversation`
- `DatabaseSchema` has many `DatabaseTable`
- `DatabaseTable` has many `DatabaseColumn`, has many `DatabaseRelationship` (source + target)
- `DatabaseColumn` has many `DatabaseRelationship` (source + target)
- `Conversation` has many `Message`, `QueryExecution`, `Clarification`
- `Conversation` stores `current_intent` as `JSONB` (the AI's `QueryAnalysis` output)
- `Conversation` tracks `current_state` via `ConversationState` enum

### 5.4 Alembic Migrations

- Config: `backend/alembic.ini` — points to `alembic/` directory
- `alembic/env.py` imports `Base.metadata` from the app and the `database_url` from settings
- The `DATABASE_URL` in `alembic.ini` is overridden at runtime by `env.py` using `settings.sqlalchemy_database_url`
- All models are imported via `import app.models.database` to ensure metadata registration
- Run: `python -m alembic upgrade head`

---

## 6. Backend (FastAPI)

### 6.1 Application Entry Point (`main.py`)

```python
configure_logging()
app = FastAPI(title="QueryMind API", version="0.1.0")

# CORS middleware (reads CORS_ORIGINS from settings)
app.add_middleware(CORSMiddleware, ...)

# Global exception handler (500 with structured error)
register_exception_handlers(app)

# Router registration
app.include_router(health_router, prefix="/api")
app.include_router(databases_router, prefix="/api")
app.include_router(queries_router, prefix="/api")
app.include_router(conversation_router, prefix="/api")
```

### 6.2 Core Module

| File | Responsibility |
|---|---|
| `config.py` | `Settings` class (Pydantic BaseSettings) — loads env vars, cached singleton |
| `errors.py` | Global `Exception` handler — returns 500 JSON with structured error logging |
| `logging.py` | `ContextFormatter` — structured log format: `timestamp level=INFO module=... request_id=... message=...` |
| `security.py` | `hash_value(value)` — SHA-256 hash utility |

### 6.3 API Endpoints

#### Health (`/api/health`)

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/api/health` | `health()` | Returns `{"status": "ok"}` |
| `GET` | `/api/health/database` | `database_health()` | Executes `SELECT 1` on the app DB |

#### Databases (`/api/databases`)

| Method | Path | Handler | Description |
|---|---|---|---|
| `POST` | `/api/databases/test` | `test_new_connection()` | Test a connection before saving (uses transient model) |
| `POST` | `/api/databases` | `create_database()` | Save a new connection (encrypts password via Fernet) |
| `GET` | `/api/databases` | `list_databases()` | List all connections (ordered by `created_at desc`) |
| `GET` | `/api/databases/{id}` | `get_database()` | Get a single connection |
| `DELETE` | `/api/databases/{id}` | `delete_database()` | Delete a connection (cascades to schemas, conversations) |
| `POST` | `/api/databases/{id}/test` | `test_saved_connection()` | Re-test a saved connection |
| `POST` | `/api/databases/{id}/introspect` | `introspect_database()` | Run live schema introspection, persist results |
| `GET` | `/api/databases/{id}/schema` | `get_schema()` | Return persisted schema as JSON |

**Important**: The `DatabaseConnectionResponse` schema **never** includes `password` or `encrypted_password`. Passwords are encrypted before storage and decrypted only when connecting.

#### Queries (`/api/databases/{id}/query`)

| Method | Path | Handler | Description |
|---|---|---|---|
| `POST` | `/api/databases/{id}/query` | `run_query()` | First-time query — creates a conversation, runs the full pipeline |
| `POST` | `/api/databases/{id}/conversations` | `create_conversation()` | Manually create a conversation |

#### Conversations (`/api/conversations`)

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/api/conversations` | `list_conversations()` | List all conversations |
| `GET` | `/api/conversations/{id}` | `get_conversation()` | Get conversation with messages and intent |
| `POST` | `/api/conversations/{id}/query` | `run_conversation_query()` | Follow-up query within a conversation |
| `POST` | `/api/conversations/{id}/clarification` | `answer_clarification()` | Answer a pending clarification question |

### 6.4 Pydantic Schemas (Request / Response)

**`schemas/databases.py`:**
- `DatabaseConnectionInput` — Input for creating/testing a connection (includes `password` field)
- `DatabaseConnectionResponse` — Response model (**excludes** password fields)
- `ConnectionTestResponse` — `{ success, message }`
- `IntrospectionResponse` — `{ success, tables, columns, relationships }`
- `ColumnResponse`, `TableResponse`, `SchemaResponse` — Nested schema representations

**`schemas/queries.py`:**
- `QueryRequest` — `{ query: str }` (1-4000 chars)
- `QueryResponse` — The universal response for all query operations:
  ```
  { status, analysis, conversation_id?, clarification?, sql?, explanation?,
    results?, result_analysis?, repair_attempts }
  ```

**`schemas/clarifications.py`:**
- `ClarificationOptionResponse` — `{ label, value }`
- `ClarificationResponse` — `{ id, field, question, options, required }`
- `ConversationQueryRequest` — `{ message }` for follow-ups
- `ClarificationAnswerRequest` — `{ clarification_id, answer }`
- `ConversationCreateRequest`, `ConversationResponse`, `ConversationHistoryResponse`

### 6.5 Services Layer (Business Logic)

This is where the core logic lives. Each service is a module-level singleton instance.

---

#### 6.5.1 `credentials.py` — Credential Encryption

```python
class CredentialService:
    def __init__(self, secret_key):
        key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str   # Fernet encrypt
    def decrypt(self, value: str) -> str   # Fernet decrypt
```

- Derives a 32-byte Fernet key from `SECRET_KEY` via SHA-256
- Used to encrypt database passwords before storage and decrypt before connecting

---

#### 6.5.2 `external_database.py` — External Database Connections

```python
class ExternalDatabaseManager:
    def _url(connection)        # Build SQLAlchemy URL (decrypting password)
    def _engine(connection)     # Create engine with pool_pre_ping, connect_timeout=5
    def test_connection(conn)   # Execute SELECT 1, return True/False
    def session(connection)     # Context manager yielding a SQLAlchemy Session
```

- **Every** external database interaction goes through this service
- Engines are disposed after each session (no persistent connection pooling to external DBs)
- `ExternalDatabaseError` wraps all external DB failures

---

#### 6.5.3 `schema_introspection.py` — Live Schema Discovery

```python
class SchemaIntrospectionService:
    def introspect(db, connection) -> dict[str, int]:
```

**Flow:**
1. Open a session to the external database
2. Use `sqlalchemy.inspect()` to enumerate:
   - Schema names (skip `pg_*` and `information_schema`)
   - Tables within each schema
   - Columns for each table (name, type, nullable, default)
   - Primary key constraints
   - Foreign key constraints
3. **Delete** any existing schema data for this connection (full refresh)
4. **Persist** new `DatabaseSchema`, `DatabaseTable`, `DatabaseColumn`, and `DatabaseRelationship` objects
5. Return summary: `{ tables: N, columns: N, relationships: N }`

This is triggered by `POST /api/databases/{id}/introspect`.

---

#### 6.5.4 `schema_serializer.py` — ORM to JSON Schema

```python
def serialize_schema(db, connection) -> dict:
```

Eagerly loads all schemas, tables, columns, and relationships for a connection and serializes them into a nested dictionary:

```json
{
  "database_id": "uuid",
  "database": "analytics",
  "dialect": "postgresql",
  "schemas": [
    {
      "name": "public",
      "tables": [
        {
          "name": "customers",
          "type": "table",
          "columns": [
            { "name": "id", "type": "INTEGER", "nullable": false,
              "primary_key": true, "foreign_key": null }
          ]
        }
      ]
    }
  ]
}
```

This dictionary is what gets passed to the AI provider and the SQL validator.

---

#### 6.5.5 `schema_retriever.py` — Keyword-Based Table Ranking

```python
class SchemaRetriever:
    def retrieve(db, database_id, query) -> list[dict]:
```

**Deterministic** (no AI needed) table ranking:

1. **Tokenize** the user query into lowercase terms (strip non-alphanumeric, remove trailing `s`)
2. **Score** each table:
   - +3 if the table name matches a query term
   - +2 per column name that matches a query term
3. **Expand** via foreign keys: add neighbor tables with score=1 (BFS traversal)
4. Return sorted list: `[{ table, score, columns }]`

This is used to **filter the schema** down to only relevant tables before passing to the AI, improving prompt quality and reducing tokens.

---

#### 6.5.6 `clarification.py` — Disambiguation Engine

Two classes:

**`ClarificationQuestionGenerator`:**
```python
def generate(analysis, schema, round_number) -> ClarificationPrompt | None:
```
- Max 3 clarification rounds
- Checks `analysis.ambiguities` for known fields:
  - `"metric"` — "How should 'best X' be measured?" with options: Highest Revenue, Most Orders, Highest Avg Order Value (schema-dependent)
  - `"time_range"` — "What time period?" with options: This Month / Quarter / Year / All Time
  - `"definition"` or `"filter"` — Generic clarification question

**`ClarificationAnswerProcessor`:**
```python
def process(clarification, answer, analysis) -> QueryAnalysis:
```
- Normalizes the answer (lowercase, underscored)
- Validates against allowed options + known aliases
- Updates the `QueryAnalysis`:
  - For `metric`: sets `analysis.metrics` and removes the metric ambiguity
  - For `time_range`: sets `analysis.time_range` and removes the time_range ambiguity
- Raises `ClarificationError` if the answer does not match any option

---

#### 6.5.7 `clarification_state.py` — Conversation State Machine

```python
class ConversationState(str, Enum):
    ANALYZING = "analyzing"
    CLARIFICATION_REQUIRED = "clarification_required"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    RESOLVING = "resolving"
    READY_FOR_SQL = "ready_for_sql"
    GENERATING_SQL = "generating_sql"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
```

State transitions are managed by the `QueryPipeline`.

---

#### 6.5.8 `sql_validator.py` — SQL Safety Gate

```python
class SQLValidator:
    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|...)\b",
        re.IGNORECASE
    )

    def validate(sql, schema) -> None:  # Raises SQLValidationError
```

**Three-layer validation:**

1. **Keyword blocking**: Reject if SQL contains `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `COMMENT`, `VACUUM`, `MERGE`, `CALL`, `COPY`, `DO`, `EXECUTE`, `PREPARE`, `SET`, or contains `--` / `/*` comments
2. **AST parsing**: Parse with `sqlglot` for PostgreSQL dialect. Reject if not exactly one `SELECT` or `UNION` statement
3. **Schema validation**:
   - Extract all `Table` references — verify each exists in the schema
   - Extract all `Column` references — resolve table aliases, verify column exists in the correct table
   - Raises `SQLValidationError` with descriptive messages like `"Table 'xxx' is not in the connected schema"`

---

#### 6.5.9 `query_executor.py` — Safe SQL Execution

```python
class QueryExecutor:
    def execute(connection, sql, schema) -> dict:
```

**Flow:**
1. **Re-validate** the SQL (calls `sql_validator.validate` again as a safety net)
2. Open a session to the external DB
3. Set `statement_timeout` to `QUERY_TIMEOUT_SECONDS * 1000` ms
4. Execute the SQL
5. Fetch up to `MAX_QUERY_ROWS` rows
6. Serialize values: `datetime` to ISO string, `Decimal` to float
7. Return: `{ columns, rows, row_count, execution_time_ms }`

**Error handling:**
- `SQLValidationError` maps to `QueryExecutionError` with `SAFETY_VIOLATION` category
- `ExternalDatabaseError` maps to `QueryExecutionError` with `CONNECTION_ERROR` category
- `SQLAlchemyError` is classified via `classify_database_error()`

---

#### 6.5.10 `error_classification.py` — Error Categorization

```python
class QueryErrorCategory(str, Enum):
    SYNTAX_ERROR, UNKNOWN_TABLE, UNKNOWN_COLUMN, INVALID_JOIN,
    INVALID_AGGREGATION, PERMISSION_ERROR, TIMEOUT, CONNECTION_ERROR,
    SAFETY_VIOLATION, UNKNOWN_DATABASE_ERROR

def classify_database_error(error) -> QueryErrorCategory:
```

Keyword-based classification of PostgreSQL error messages (timeout, permission, column/relation does not exist, etc.)

---

#### 6.5.11 `sql_repair.py` — Bounded SQL Repair

```python
class SQLRepairService:
    def repair(sql, error, schema) -> str:
```

- **Deliberately conservative**: only normalizes trailing semicolons
- Re-validates the repaired SQL through the validator
- Raises `SQLRepairError` if the repair fails validation
- The pipeline retries up to `MAX_SQL_REPAIR_ATTEMPTS` times

---

#### 6.5.12 `result_analyzer.py` — Result Analysis and Chart Recommendation

```python
class ResultAnalyzer:
    def analyze(columns, rows) -> dict:
```

**Column classification:**
- **Numeric**: All non-null values are `int`, `float`, or `Decimal`
- **Temporal**: Column name contains "date" (or is in known set: `date`, `month`, `year`, `created_at`, `order_date`)
- **Categorical**: String-typed columns not classified as temporal

**Visualization recommendation:**

| Condition | Chart Type |
|---|---|
| 1 row + 1 numeric column | `KPI` (single value display) |
| Has temporal + numeric | `LINE` chart |
| Has categorical + numeric (100 rows or less) | `BAR` chart |
| Everything else | `TABLE` |

Returns:
```json
{
  "row_count": 10,
  "numeric_columns": ["revenue"],
  "temporal_columns": ["month"],
  "categorical_columns": ["customer_name"],
  "visualization": { "type": "BAR", "x": "customer_name", "y": "revenue" },
  "summary": "Returned 10 rows. revenue ranges from 360 to 628."
}
```

---

#### 6.5.13 `intent_modifier.py` — Follow-Up Intent Mutations

```python
class IntentModifier:
    def apply(analysis, follow_up) -> QueryAnalysis:
```

Pattern-matched modifications to an existing `QueryAnalysis`:
- `"top N"` sets `analysis.limit = N`
- `"last year"` sets time_range to previous calendar year
- `"this year"` sets time_range to current calendar year
- `"north"` adds region filter for "North America"

This enables conversational follow-ups like "Make that top 20" or "Only for the North region".

---

### 6.6 AI Module

#### 6.6.1 Data Models (`ai/models.py`)

```python
class Metric(BaseModel):         # name, definition, expression_hint
class TimeRange(BaseModel):      # type, year, start, end
class SortSpec(BaseModel):       # field, direction (asc/desc)
class Ambiguity(BaseModel):      # field, reason

class QueryAnalysis(BaseModel):
    intent: str                  # e.g., "customer_revenue", "monthly_revenue"
    entities: list[str]          # e.g., ["customers", "orders"]
    metrics: list[Metric]
    dimensions: list[str]
    filters: list[dict]
    time_range: TimeRange | None
    sort: SortSpec | None
    limit: int | None
    is_ambiguous: bool
    ambiguities: list[Ambiguity]

class SQLGenerationResult(BaseModel):
    sql: str                     # The generated SELECT statement
    explanation: str             # Human-readable explanation
    tables_used: list[str]       # Tables referenced
```

#### 6.6.2 Provider Interface (`ai/provider.py`)

```python
class AIProvider(ABC):
    async def analyze_query(query, schema, dialect) -> QueryAnalysis
    async def generate_sql(query, analysis, schema, dialect) -> SQLGenerationResult
```

Two abstract methods that both providers must implement.

#### 6.6.3 Factory (`ai/factory.py`)

```python
def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "openai":
        return OpenAIProvider()
    return MockAIProvider()  # default fallback
```

#### 6.6.4 Mock Provider (`ai/mock_provider.py`)

Deterministic, no-API-call provider for local development and testing:

**`analyze_query()`:**
- `"active"` in query — ambiguous (`definition` field, schema does not define "active")
- `"best"` or `"good"` — ambiguous (`metric` field, could be revenue, count, avg)
- `"month"` or `"monthly"` — clear intent: monthly revenue aggregation
- Default — customer revenue ranking (top 10, current year)

**`generate_sql()`:**
- Monthly revenue: `SELECT DATE_TRUNC('month', ...) GROUP BY 1 ORDER BY 1`
- Products: `SELECT p.name, SUM(oi.quantity * oi.unit_price) FROM products p JOIN ...`
- Default: `SELECT c.name, SUM(o.total_amount) FROM customers c JOIN orders o ...`
- Supports region filter and dynamic LIMIT

#### 6.6.5 OpenAI Provider (`ai/openai_provider.py`)

Real API integration via `httpx`:

```python
class OpenAIProvider(AIProvider):
    endpoint = "https://api.openai.com/v1/chat/completions"

    async def _complete(prompt) -> dict:
        # POST to OpenAI with temperature=0, JSON response format
        # Parses the JSON content from the response
```

- Uses system prompts from `ai/prompts/` to structure requests
- `analyze_query()` sends the query + schema, expects `QueryAnalysis` JSON
- `generate_sql()` sends the query + analysis + schema, expects `SQLGenerationResult` JSON

#### 6.6.6 System Prompts (`ai/prompts/`)

| Prompt | Purpose |
|---|---|
| `query_analysis.py` | "Analyze the NL question using only the supplied schema. Return QueryAnalysis JSON. Detect ambiguity. Do not generate SQL." |
| `sql_generation.py` | "Generate one read-only PostgreSQL query. Return SQLGenerationResult JSON. Only SELECT/WITH." |
| `clarification_detection.py` | "Identify material ambiguities in intent. Use schema only." |
| `clarification_question.py` | "Create one short clarification question with schema-supported options." |
| `clarification_answer.py` | "Map the user's answer to one supplied option or return invalid." |

---

## 7. The Query Pipeline — End-to-End Flow

The `QueryPipeline` class in `services/query_pipeline.py` is the **central orchestrator**. It has three entry points:

### 7.1 First Query: `pipeline.run(db, connection, query)`

```
User types: "Show the top 10 customers by revenue this year."
         |
1. Create Conversation (state = ANALYZING)
2. Save user Message
3. Call _start()
         |
4. Serialize the persisted schema to JSON
5. Schema Retriever: rank tables by keyword match
6. Filter schema to relevant tables only
7. AI Provider: analyze_query(query, schema, "postgresql")
         |
   Returns QueryAnalysis:
   {
     intent: "customer_revenue",
     entities: ["customers", "orders"],
     metrics: [{ name: "revenue", definition: "sum of order total amount" }],
     time_range: { type: "calendar_year", year: 2026 },
     sort: { field: "revenue", direction: "desc" },
     limit: 10,
     is_ambiguous: false
   }
         |
8. NOT ambiguous -> proceed to _execute_resolved()
         |
9. AI Provider: generate_sql(query, analysis, schema, "postgresql")
         |
   Returns SQLGenerationResult:
   {
     sql: "SELECT c.name AS customer_name, SUM(o.total_amount) AS total_revenue
           FROM customers c JOIN orders o ON c.id = o.customer_id
           WHERE o.order_date >= '2026-01-01' AND o.order_date < '2027-01-01'
           GROUP BY c.id, c.name ORDER BY total_revenue DESC LIMIT 10;",
     explanation: "Joins customers and orders, calculates total revenue.",
     tables_used: ["customers", "orders"]
   }
         |
10. SQL Validator: parse with sqlglot, check for safety + schema compliance
         |
11. Query Executor:
    - SET statement_timeout = 10000
    - Execute the SQL on the external DB
    - Fetch up to 1000 rows
    - Convert Decimals/dates to JSON-serializable values
         |
   Returns: { columns: [...], rows: [[...]], row_count: 3, execution_time_ms: 47 }
         |
12. Result Analyzer: classify columns, recommend visualization
         |
   Returns: { visualization: { type: "BAR", x: "customer_name", y: "total_revenue" },
              summary: "..." }
         |
13. Persist QueryExecution record (status=completed)
14. Set Conversation state = COMPLETED
15. Return QueryResponse to API -> Frontend
```

### 7.2 Ambiguous Query: Clarification Flow

```
User types: "Show me the best customers."
         |
Steps 1-7 (same as above)
         |
   QueryAnalysis.is_ambiguous = True
   ambiguities: [{ field: "metric", reason: "best could mean revenue, count..." }]
         |
8. ClarificationQuestionGenerator.generate():
   -> "How should 'best customers' be measured?"
   -> Options: [Highest Revenue, Most Orders, Highest Average Order Value]
         |
9. _save_clarification():
   - Set Conversation state = WAITING_FOR_ANSWER
   - Create Clarification record (field=metric, options=[...])
   - Save assistant Message with the question
   - Return response with status="clarification_required"
         |
   Frontend displays ClarificationCard with options
         |
User clicks "Highest Revenue"
         |
POST /api/conversations/{id}/clarification { clarification_id, answer: "revenue" }
         |
10. pipeline.answer():
    - Validate conversation is in WAITING_FOR_ANSWER state
    - ClarificationAnswerProcessor.process():
      - Normalize answer -> "revenue"
      - Set analysis.metrics = [Metric(name="revenue", ...)]
      - Remove metric ambiguity
    - Check for remaining ambiguities (e.g., time_range)
    - If no more ambiguities -> proceed to _execute_resolved()
         |
Steps 9-15 (SQL generation -> execution -> analysis -> response)
```

### 7.3 Follow-Up Query (Conversation Continuation)

```
Previous conversation completed with: "Show top 10 customers by revenue this year"
         |
User types: "Make that top 20."
         |
POST /api/conversations/{id}/query { message: "Make that top 20." }
         |
1. pipeline.start():
   - Conversation state is COMPLETED and has current_intent
   - IntentModifier.apply(): parse "top 20" -> set analysis.limit = 20
   - Create new QueryExecution with modified analysis
   - Call _execute_resolved() (re-generates SQL with new limit)
         |
Steps 9-15 (new SQL with LIMIT 20 -> execution -> response)
```

### 7.4 SQL Repair Flow

```
During _execute_resolved():
         |
Query Executor raises QueryExecutionError
         |
while repair_attempts < MAX_SQL_REPAIR_ATTEMPTS:
    SQLRepairService.repair(sql, error, schema)
    Query Executor.execute(repaired_sql)
    if succeeds -> break (save repaired_sql)
         |
If all repair attempts fail:
    Set error_category on execution record
    Raise QueryPipelineError
```

---

## 8. Frontend (React + Vite)

### 8.1 Entry Point and Routing

**`main.tsx`:**
- Creates a TanStack `QueryClient`
- Wraps the app in `QueryClientProvider` then `BrowserRouter` then `App`
- Imports three CSS files: `styles.css`, `database.css`, `phase5.css`

**`App.tsx`:**
- Renders a sidebar + main content layout
- Sidebar: Brand logo ("Q" + "QueryMind"), navigation links (Dashboard, Databases, Conversations), footer
- Routes:
  - `/` renders `Dashboard`
  - `/databases` renders `DatabasePage`
  - `/conversations` renders `ConversationsPage`
- Uses Lucide icons: `LayoutDashboard`, `Database`, `MessageSquare`, `BarChart3`

### 8.2 Pages

#### `Dashboard.tsx` — Main Query Workspace

The primary user interface for asking questions:

**State:**
- `databases` — Connected databases (fetched on mount, filtered to `connected` status)
- `databaseId` — Currently selected database
- `query` — User's natural language question
- `result` — The `QueryResponse` from the backend
- `conversationId` — Active conversation (enables follow-ups)
- `loading`, `error` — UI state

**Key flows:**
1. On mount: fetch `/databases` to populate database selector
2. On submit:
   - If `conversationId` exists: `POST /conversations/{id}/query` (follow-up)
   - Else: `POST /databases/{id}/query` (new query)
3. If response has `status: "clarification_required"`: show `ClarificationCard`
4. If response has `status: "completed"`: show success banner, `SQLViewer`, `ResultVisualization`, `ResultTable`
5. On clarification answer: `POST /conversations/{id}/clarification`

**Layout:** Hero section ("Ask better questions of your data"), query input form with database selector, results area, grid with recent conversations and quick start guide.

#### `DatabasePage.tsx` — Connection Management

Full CRUD for database connections:

**Features:**
- "Add Database" button opens an expandable form (name, host, port, database, username, password, SSL mode)
- "Test Connection" calls `POST /databases/test` (before saving)
- "Save Database" calls `POST /databases`
- Database cards: each shows connection details, status pill (connected/untested/failed)
- Card actions: Test Connection, View Schema, Refresh Schema, Delete
- Schema section: appears when a database is selected
  - Calls `POST /databases/{id}/introspect` then `GET /databases/{id}/schema`
  - Renders `SchemaExplorer` component

#### `ConversationsPage.tsx` — History

- Fetches `GET /conversations` on mount
- Renders a list of conversation cards with title, state, and timestamp
- Empty state: "No conversations yet."

#### `PlaceholderPage.tsx`

Generic placeholder component with an icon, eyebrow text, title, and description.

### 8.3 Components

#### `ClarificationCard.tsx`
- Displays the AI's clarification question
- Renders option buttons (each triggers `onAnswer(option.value)`)
- Has a free-text input for custom answers
- Styled with a warm amber border-left accent

#### `ResultTable.tsx`
- Loading state: spinner + "Running query..."
- Error state: red error text
- Empty state: "No rows returned."
- Data state: HTML table with headers + rows, `NULL` values displayed as "NULL"

#### `ResultVisualization.tsx`
- Reads the `analysis.visualization` recommendation
- If type is `TABLE` or missing x/y: renders nothing
- `LINE` type renders a `<LineChart>` from Recharts (green line, `#71994a`)
- `BAR` type renders a `<BarChart>` from Recharts (green bars, `#98ba61`)
- Wrapped in `ResponsiveContainer` (100% width, 270px height)

#### `SQLViewer.tsx`
- Collapsible section showing the generated SQL
- "Copy" button copies SQL to clipboard
- Dark background (`#1d2925`) with green code text (`#d3e8a1`)

#### `SchemaExplorer.tsx`
- Two-panel layout: schema tree (left) + table details (right)
- **Tree view**: Schema then Tables then Columns (expandable/collapsible)
  - Primary keys shown with `KeyRound` icon
  - Foreign keys shown with `GitBranch` icon
  - Regular columns shown with `Columns3` icon
- **Detail view**: Column table (name, type, nullable), primary key summary, foreign key summary

### 8.4 Services and Types

**`services/api.ts`:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T>
```
- Generic fetch wrapper
- Adds `Content-Type: application/json` header
- Throws `ApiError(status, message)` on non-OK responses

### 8.5 Styling

The frontend uses a combination of **vanilla CSS** and **Tailwind CSS**:

- **Typography**: DM Sans (body) + Space Grotesk (headings) from Google Fonts
- **Color palette**: Earthy green/olive tones
  - `#17201e` (dark text)
  - `#f5f7f2` (background)
  - `#b8d76a` (primary accent)
  - `#6e9740` (green)
  - `#d29a5d` (amber for clarifications)
- **Layout**: CSS flex/grid, sidebar (248px) + main content
- **Responsive**: Media queries at 700px and 500px for mobile
- CSS is split across three files:
  - `styles.css` — Global layout, sidebar, dashboard, query workspace
  - `database.css` — Database page, form, cards, schema explorer
  - `phase5.css` — Visualizations, clarification cards, conversations

---

## 9. Security Model

| Layer | Measure |
|---|---|
| **Credential Storage** | Database passwords encrypted with Fernet (AES-128-CBC) before storage. Decrypted only at connection time. |
| **API Responses** | `DatabaseConnectionResponse` explicitly excludes `password` and `encrypted_password` fields. |
| **SQL Safety** | Three-layer validation: keyword blocking, then AST parsing (single SELECT/UNION), then schema validation (tables + columns). |
| **Forbidden Operations** | `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, comments (`--`, `/*`), multi-statement SQL — all rejected. |
| **Query Limits** | `statement_timeout` on external queries (configurable, default 10s). `MAX_QUERY_ROWS` limit (default 1000). |
| **AI Validation** | All AI responses are validated through Pydantic models. |
| **Clarification Validation** | Answers must match schema-supported options or recognized intent values. |
| **Error Handling** | Global exception handler catches unhandled errors and returns generic 500 (no stack traces to client). |
| **CORS** | Configurable origin list (only frontend origins allowed). |

---

## 10. Testing

The backend has **6 test files** covering different aspects:

| Test File | What It Tests |
|---|---|
| `test_health.py` | Health endpoint returns 200 + `{"status": "ok"}` |
| `test_phase1.py` | Credential encryption round-trip, response model excludes password |
| `test_ai_pipeline.py` | Mock provider: analyzes customer revenue, marks "best" as ambiguous, generates read-only SQL |
| `test_clarification.py` | Question generator produces correct options, answer processor updates analysis, invalid answers rejected, stops after 3 rounds |
| `test_intelligence.py` | Result analyzer recommends LINE chart, handles empty results, follow-up changes limit/time, validator rejects comments/multi-statements, error classifier categorizes timeout |
| `test_query_safety.py` | SQL validator allows SELECT, rejects DROP/DELETE/UPDATE/INSERT/multi-statement, rejects unknown columns |

**Run tests:**
```bash
cd backend
python -m pytest
```

---

## 11. Evaluation Dataset

`evaluation/queries.json` contains **47 test cases** across 7 categories:

| Category | Count | Examples | Expected Outcome |
|---|---|---|---|
| **Clear queries** | 3 | "Show top 10 customers by revenue this year" | `completed` |
| **Schema-dependent** | 16 | "Show order totals by region", "List all customers" | `completed_or_schema_limited` |
| **Ambiguous** | 10 | "Show the best customers", "Show active customers" | `clarification_required` |
| **Follow-ups** | 5 | "Make that top 20", "Only for the North region" | `follow_up_*` |
| **Unsafe SQL** | 5 | `DROP TABLE`, `DELETE FROM`, SQL injection | `rejected` |
| **Schema violations** | 2 | `SELECT missing_column`, `SELECT * FROM missing_table` | `schema_rejected` |
| **Repair candidates** | 3 | Valid table but bad column filter | `repair_candidate` |

---

## 12. How to Run

### Docker (Recommended)

```powershell
# 1. Copy environment template
Copy-Item .env.example .env

# 2. Set a strong SECRET_KEY in .env

# 3. Start everything
docker compose up --build -d

# Services:
# - QueryMind DB:     localhost:5432
# - Demo DB:          localhost:5433
# - Backend API:      http://localhost:8000  (docs at /docs)
# - Frontend:         http://localhost:5173
```

### Local Development

```powershell
# Start databases only
docker compose up -d postgres demo-postgres

# Backend (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

### First-Time Usage Flow

1. Open `http://localhost:5173`
2. Go to **Databases** and click **Add Database**
3. Enter demo credentials: `localhost` / `5433` / `analytics` / `analyst` / `analyst`
4. Click **Test Connection** then **Save Database**
5. Click **View Schema** — the schema tree populates
6. Go to **Dashboard** and select the database
7. Type: "Show the top 10 customers by revenue this year"
8. See: generated SQL, results table, bar chart visualization

---

*This documentation covers the complete QueryMind project as of its current state. Every file, service, component, and data flow has been documented above.*
