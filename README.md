# VectorVault

**Secure semantic knowledge and retrieval infrastructure for documents.**

VectorVault is a developer-facing platform for uploading knowledge documents, organizing them into tenant-isolated collections, searching them semantically, and asking grounded questions with source references. It is an explainable modular monolith with production-minded boundaries.

## The problem

Traditional keyword search misses meaning: a search for "protect API keys" may not find a document titled "Credential Storage Policy." Adding AI to internal documents also introduces serious risks: one workspace must never retrieve another workspace's data, uploaded content is untrusted, and answers must not invent unsupported facts.

VectorVault addresses this through document embeddings, metadata-filtered vector retrieval, PostgreSQL metadata, and server-side workspace authorization before every protected operation.

## Features

- Upload and ingest PDF, TXT, and Markdown documents.
- Create workspaces and collections with owner/member roles.
- Chunk text, generate embeddings, and index every chunk.
- Use Pinecone in production or an in-memory VectorStore for local development/tests.
- Run tenant-scoped semantic search with collection and metadata filters.
- Ask grounded questions and receive retrieved source chunks.
- Register/login with Argon2 password hashing and signed access/refresh tokens.
- Create and revoke owner-managed API keys; raw keys are shown only once and only hashes are stored.
- Validate upload size and MIME type, prevent duplicate uploads by checksum, and track ingestion status.
- Start PostgreSQL, Redis, and FastAPI locally with Docker Compose.
- Explore API routes through automatic Swagger documentation.

## Architecture

```mermaidnn
flowchart LR
  UI["Next.js dashboard"] --> API["FastAPI /api/v1"]
  API --> DB[("PostgreSQL metadata")]
  API --> SVC["Ingestion, Search & RAG services"]
  SVC --> EMB["EmbeddingProvider"]
  SVC --> VS["VectorStore"]
  VS --> PC["Pinecone (production)"]
  API --> REDIS["Redis (rate limits/cache roadmap)"]
```

PostgreSQL remains the source of truth for identities and document metadata. Pinecone is the intended production vector database. The `VectorStore` interface enables a local in-memory implementation for tests and local demos without cloud credentials.

## Quick start with Docker

### Prerequisites

- Docker Desktop running
- Git (only required to clone or push the repository)

### Run locally

```powershell
Copy-Item .env.example .env
docker compose up --build
```

When the API log says `Uvicorn running on http://0.0.0.0:8000`, open:

- [Swagger API documentation](http://localhost:8000/docs)
- [Health endpoint](http://localhost:8000/api/v1/health)

Stop the stack with `docker compose down`.

## First API workflow

1. `POST /api/v1/auth/register` to create an account.
2. Copy the access token from the response and click **Authorize** in Swagger.
3. `POST /api/v1/workspaces` to create a workspace.
4. `POST /api/v1/collections` using that workspace ID.
5. Upload a PDF, TXT, or Markdown file through `POST /api/v1/documents/upload`.
6. Call `POST /api/v1/search` or `POST /api/v1/query` with the workspace ID.

## Environment configuration

Start from [`.env.example`](.env.example). Local mode is credential-free:

```dotenv
VECTOR_STORE=local
EMBEDDING_PROVIDER=local
```

For cloud vector search:

```dotenv
VECTOR_STORE=pinecone
PINECONE_API_KEY=your-key
PINECONE_INDEX=your-index
```

For OpenAI embeddings:

```dotenv
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Never commit `.env` or real secrets.

## Technology choices

| Technology | Why it is used |
| --- | --- |
| FastAPI | Typed REST APIs, Pydantic validation, automatic OpenAPI docs. |
| PostgreSQL | Relational source of truth, constraints, and tenant metadata. |
| Pinecone | Managed production vector storage and metadata-filtered similarity search. |
| Redis | Reserved for distributed rate limits and targeted caching. |
| Docker Compose | Reproducible local API, database, and Redis environment. |
| Next.js | Minimal dashboard foundation for operators. |

Pinecone is the production vector choice; local storage is useful for fast development, and pgvector is a strong alternative when consolidating vector and relational operations in PostgreSQL is more important than a dedicated managed vector service.

## Security model

- Passwords are Argon2 hashed; plaintext passwords are never stored.
- Server-side workspace checks protect documents, search results, collections, and API keys.
- Only workspace owners can revoke keys or delete collections.
- API keys are generated with secure randomness and stored as hashes.
- Uploads are allowlisted by MIME type and limited by size; filenames are not used as file paths.
- Retrieved content is treated as untrusted data, not as system instructions.

See [Security](docs/SECURITY.md) for implemented controls, limitations, and recommended next steps.

## Repository structure

```text
backend/app/       FastAPI API, models, services, providers
frontend/          Minimal Next.js dashboard
tests/             Unit-test foundation
evaluation/        Synthetic retrieval-evaluation fixture
sample_documents/  Safe demo documents
docs/              Design, API, security, and project documentation
migrations/        Alembic migration scaffold
```

## Testing and quality

```powershell
pip install -e ".[dev]"
pytest
ruff check .
```

The current test suite covers chunking and tenant-aware local vector filtering. Expand it before production use with API, database, authorization, and cloud-adapter integration tests.

## Documentation

- [System design](docs/SYSTEM_DESIGN.md)
- [Database design](docs/DATABASE_DESIGN.md)
- [Data pipeline](docs/DATA_PIPELINE.md)
- [API guide](docs/API_GUIDE.md)
- [Security](docs/SECURITY.md)
- [Operations](docs/OPERATIONS.md)
- [Final project report](docs/FINAL_PROJECT_REPORT.md)

## Current limitations and roadmap

This repository does not claim finished production operations. Immediate priorities are durable asynchronous ingestion, Redis-backed rate limiting, production Alembic migrations, persistent object storage, full API-key authentication middleware, metrics, and cloud integration tests with real Pinecone/OpenAI credentials.

## License

MIT. See [LICENSE](LICENSE).
