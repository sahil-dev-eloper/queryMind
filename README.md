# QueryMind

QueryMind is a natural-language analytics application for PostgreSQL databases. Connect a database, inspect its schema, ask questions in plain English, and receive safe SQL, real results, summaries, and visualizations.

## Features

- PostgreSQL database connection management
- Encrypted database credentials
- Automatic schema introspection
- Tables, columns, primary keys, and foreign-key relationships
- Deterministic schema retrieval
- Mock AI provider for local development and testing
- OpenAI-compatible provider support
- Natural-language to PostgreSQL SQL generation
- Targeted clarification questions for ambiguous requests
- Stateful multi-turn clarification conversations
- Read-only SQL validation and schema validation
- Query timeouts and result row limits
- SQL error classification and bounded repair handling
- Result summaries and automatic chart recommendations
- Dynamic table, line-chart, bar-chart, and KPI displays
- Conversation history and follow-up queries
- Seeded demo PostgreSQL database

## Architecture

```mermaid
flowchart TD
    UI[React Frontend] --> API[FastAPI API]
    API --> CM[Conversation and Query Pipeline]
    CM --> SR[Schema Retriever]
    SR --> CE[Clarification Engine]
    CE -->|resolved intent| SG[SQL Generator]
    SG --> SV[SQL and Schema Validator]
    SV --> EX[Read-only SQL Executor]
    EX --> RA[Result Analyzer]
    RA --> UI
    CM --> APPDB[(Application PostgreSQL)]
    EX --> EXTDB[(External PostgreSQL)]
```

The application database stores QueryMind data such as connections, conversations, messages, schema metadata, and query executions. User-connected PostgreSQL databases remain separate and are used only for schema inspection and validated read-only queries.

## Technology Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, Lucide React
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- Databases: PostgreSQL
- AI: Mock provider and OpenAI-compatible provider
- Infrastructure: Docker and Docker Compose

## Requirements

- Python 3.12 or newer
- Node.js 22 or newer
- npm
- Docker Desktop with the Linux container engine enabled

## Quick Start With Docker

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Set a strong `SECRET_KEY` in `.env`.

3. Start the complete environment:

   ```powershell
   docker compose up --build -d
   ```

This starts:

- QueryMind PostgreSQL on `localhost:5432`
- The seeded demo PostgreSQL database on `localhost:5433`
- FastAPI on `http://localhost:8000`
- React/Vite on `http://localhost:5173`

The backend container runs database migrations automatically.

## Demo Database

The demo database is seeded with:

- `customers`
- `orders`
- `order_items`
- `products`
- `categories`
- `regions`

From the host, use:

```text
Host: localhost
Port: 5433
Database: analytics
Username: analyst
Password: analyst
SSL mode: prefer
```

When connecting from the backend container, use host `demo-postgres` and port `5432`.

## Local Development

Start the databases:

```powershell
docker compose up -d postgres demo-postgres
```

Set up the backend:

```powershell
cd backend
python -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set up the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open `http://localhost:5173`.

## Configuration

Copy `.env.example` to `.env` and configure:

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://querymind:querymind@localhost:5432/querymind
SECRET_KEY=replace-with-a-long-random-value
AI_PROVIDER=mock
AI_API_KEY=
AI_MODEL=
MAX_QUERY_ROWS=1000
QUERY_TIMEOUT_SECONDS=10
MAX_SQL_REPAIR_ATTEMPTS=2
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Use `AI_PROVIDER=mock` for deterministic local operation. To use the OpenAI-compatible provider, set `AI_PROVIDER=openai`, `AI_API_KEY`, and `AI_MODEL`. Secrets are read only by the backend and are not exposed to frontend code.

## Common API Endpoints

```text
GET  /api/health
GET  /api/health/database

POST /api/databases/test
POST /api/databases
GET  /api/databases
GET  /api/databases/{database_id}
DELETE /api/databases/{database_id}
POST /api/databases/{database_id}/test
POST /api/databases/{database_id}/introspect
GET  /api/databases/{database_id}/schema
POST /api/databases/{database_id}/query

GET  /api/conversations
GET  /api/conversations/{conversation_id}
POST /api/conversations/{conversation_id}/query
POST /api/conversations/{conversation_id}/clarification
```

Interactive API documentation is available at `http://localhost:8000/docs`.

Example query request:

```json
{
  "query": "Show the top 10 customers by revenue this year."
}
```

Example follow-up request:

```json
{
  "message": "What about last year?"
}
```

## Example Questions

- Show the top 10 customers by revenue this year.
- Show monthly revenue for 2026.
- Which products generated the most revenue?
- Show me the best customers.
- Make that top 20.
- Only for the North region.

When a question is materially ambiguous, QueryMind asks a targeted question instead of guessing. For example, “Show me the best customers” can be resolved with “Highest Revenue”, “Most Orders”, or “Highest Average Order Value”.

## Security

- Database passwords are encrypted before storage.
- Passwords and API keys are excluded from API responses and logs.
- SQL is parsed and restricted to one read-only statement.
- Write, destructive, administrative, comment, and multi-statement SQL is rejected.
- Referenced tables and columns are checked against persisted schema metadata.
- External queries use a statement timeout and maximum row limit.
- AI responses are validated with Pydantic models.
- Clarification answers must match schema-supported options or recognized intent values.

## Database Migrations

Run migrations from the `backend` directory:

```powershell
python -m alembic upgrade head
python -m alembic current
```

## Testing

Backend tests:

```powershell
cd backend
python -m pytest
```

Frontend production build:

```powershell
cd frontend
npm run build
```

The evaluation behavior dataset is stored in [evaluation/queries.json](evaluation/queries.json). It covers clear questions, ambiguity, follow-ups, unsafe SQL, schema validation, and repair scenarios.

## Project Structure

```text
QueryMind/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── tests/
├── demo/
├── evaluation/
├── frontend/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Current Scope

The application includes the core natural-language analytics workflow, clarification, safe SQL execution, result analysis, visualization, and conversation follow-ups. Advanced semantic SQL repair, authentication, multi-user authorization, embeddings, and vector-based retrieval are outside the current scope.
